package com.kartikeyajhamnani_017.nexus.product_service.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;

public record ProductRequest(
        @NotBlank(message = "name must not be blank") String name,
        String description,
        @NotNull(message = "price is required")
        @DecimalMin(value = "0.0", inclusive = true, message = "price must not be negative") BigDecimal price
) {
}
