package com.kartikeyajhamnani_017.nexus.order_service.service;

import com.kartikeyajhamnani_017.nexus.order_service.dto.OrderRequest;
import com.kartikeyajhamnani_017.nexus.order_service.entity.Order;
import com.kartikeyajhamnani_017.nexus.order_service.exception.OrderNotFoundException;
import com.kartikeyajhamnani_017.nexus.order_service.messaging.OrderEventPublisher;
import com.kartikeyajhamnani_017.nexus.order_service.repository.OrderRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class OrderService {

    private static final Logger log = LoggerFactory.getLogger(OrderService.class);

    private final OrderRepository orderRepository;
    private final OrderEventPublisher orderEventPublisher;

    public OrderService(OrderRepository orderRepository, OrderEventPublisher orderEventPublisher) {
        this.orderRepository = orderRepository;
        this.orderEventPublisher = orderEventPublisher;
    }

    @Transactional
    public Order createOrder(OrderRequest request) {
        Order order = new Order(request.productId(), request.quantity());
        Order saved = orderRepository.save(order);
        log.info("order.created orderId={} productId={} quantity={}",
                saved.getId(), saved.getProductId(), saved.getQuantity());
        orderEventPublisher.publishOrderPlaced(saved);
        return saved;
    }

    public Order getOrder(Long id) {
        return orderRepository.findById(id)
                .orElseThrow(() -> new OrderNotFoundException(id));
    }
}
