package com.kartikeyajhamnani_017.nexus.order_service.messaging;

import com.kartikeyajhamnani_017.nexus.order_service.entity.Order;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Component;

import java.time.Instant;

@Component
public class OrderEventPublisher {

    private static final Logger log = LoggerFactory.getLogger(OrderEventPublisher.class);

    private final RabbitTemplate rabbitTemplate;

    public OrderEventPublisher(RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public void publishOrderPlaced(Order order) {
        OrderPlacedEvent event = new OrderPlacedEvent(
                order.getId(), order.getProductId(), order.getQuantity(), Instant.now());
        try {
            rabbitTemplate.convertAndSend(event);
            log.info("event.published orderId={} productId={} quantity={}",
                    order.getId(), order.getProductId(), order.getQuantity());
        } catch (Exception ex) {
            log.error("event.publish.failed orderId={} reason={}", order.getId(), ex.getMessage(), ex);
            throw ex;
        }
    }
}
