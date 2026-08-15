package com.kartikeyajhamnani_017.nexus.product_service.exception;

public class ProductNotFoundException extends RuntimeException {
    public ProductNotFoundException(String id) {
        super("Product not found: " + id);
    }
}
