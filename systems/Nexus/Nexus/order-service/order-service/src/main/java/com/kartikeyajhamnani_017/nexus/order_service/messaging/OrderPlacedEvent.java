package com.kartikeyajhamnani_017.nexus.order_service.messaging;

import java.io.Serializable;
import java.time.Instant;

public record OrderPlacedEvent(
        Long orderId,
        String productId,
        int quantity,
        Instant occurredAt
) implements Serializable {
}
