package com.kartikeyajhamnani_017.nexus.inventory_service.exception;

public class InventoryAlreadyExistsException extends RuntimeException {
    public InventoryAlreadyExistsException(String productId) {
        super("Inventory already seeded for productId: " + productId);
    }
}
