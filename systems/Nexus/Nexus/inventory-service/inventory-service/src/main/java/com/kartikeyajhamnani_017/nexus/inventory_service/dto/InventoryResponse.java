package com.kartikeyajhamnani_017.nexus.inventory_service.dto;

import com.kartikeyajhamnani_017.nexus.inventory_service.entity.Inventory;

import java.time.Instant;

public record InventoryResponse(
        String productId,
        int stock,
        Instant updatedAt
) {
    public static InventoryResponse from(Inventory inventory) {
        return new InventoryResponse(inventory.getProductId(), inventory.getStock(), inventory.getUpdatedAt());
    }
}
