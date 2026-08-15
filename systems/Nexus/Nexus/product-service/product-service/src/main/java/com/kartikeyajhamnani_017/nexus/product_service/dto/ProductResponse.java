package com.kartikeyajhamnani_017.nexus.product_service.dto;

import com.kartikeyajhamnani_017.nexus.product_service.document.Product;

import java.math.BigDecimal;

public record ProductResponse(
        String id,
        String name,
        String description,
        BigDecimal price
) {
    public static ProductResponse from(Product product) {
        return new ProductResponse(product.getId(), product.getName(), product.getDescription(), product.getPrice());
    }
}
