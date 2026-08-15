package com.kartikeyajhamnani_017.nexus.inventory_service.messaging;

import com.kartikeyajhamnani_017.nexus.inventory_service.service.InventoryService;
import com.rabbitmq.client.Channel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.amqp.support.AmqpHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Component;

import java.io.IOException;

@Component
public class OrderEventListener {

    private static final Logger log = LoggerFactory.getLogger(OrderEventListener.class);

    private final InventoryService inventoryService;

    public OrderEventListener(InventoryService inventoryService) {
        this.inventoryService = inventoryService;
    }

    @RabbitListener(queues = RabbitMQConfig.QUEUE)
    public void onOrderPlaced(@Payload OrderPlacedEvent event,
                               Channel channel,
                               @Header(AmqpHeaders.DELIVERY_TAG) long deliveryTag) throws IOException {
        log.info("event.consumed orderId={} productId={} quantity={}",
                event.orderId(), event.productId(), event.quantity());
        try {
            boolean applied = inventoryService.applyOrderDecrement(event.productId(), event.quantity());
            if (applied) {
                log.info("inventory.stock.updated orderId={} productId={} quantity={}",
                        event.orderId(), event.productId(), event.quantity());
            } else {
                log.warn("inventory.stock.insufficient_or_missing orderId={} productId={} quantity={}",
                        event.orderId(), event.productId(), event.quantity());
            }
            // Business-level outcomes (missing record, insufficient stock) still ack -
            // they are not infrastructure failures and must not be retried forever.
            channel.basicAck(deliveryTag, false);
        } catch (Exception ex) {
            log.error("inventory.stock.update_failed orderId={} productId={} reason={}",
                    event.orderId(), event.productId(), ex.getMessage(), ex);
            throw ex;
        }
    }
}
