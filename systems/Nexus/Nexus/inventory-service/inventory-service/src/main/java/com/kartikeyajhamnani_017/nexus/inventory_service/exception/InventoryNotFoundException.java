package com.kartikeyajhamnani_017.nexus.inventory_service.exception;

public class InventoryNotFoundException extends RuntimeException {
    public InventoryNotFoundException(String productId) {
        super("No inventory record for productId: " + productId);
    }
}
