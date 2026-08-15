package com.kartikeyajhamnani_017.nexus.order_service.dto;

import com.kartikeyajhamnani_017.nexus.order_service.entity.Order;
import com.kartikeyajhamnani_017.nexus.order_service.entity.OrderStatus;

import java.time.Instant;

public record OrderResponse(
        Long id,
        String productId,
        int quantity,
        OrderStatus status,
        Instant createdAt
) {
    public static OrderResponse from(Order order) {
        return new OrderResponse(
                order.getId(),
                order.getProductId(),
                order.getQuantity(),
                order.getStatus(),
                order.getCreatedAt()
        );
    }
}
