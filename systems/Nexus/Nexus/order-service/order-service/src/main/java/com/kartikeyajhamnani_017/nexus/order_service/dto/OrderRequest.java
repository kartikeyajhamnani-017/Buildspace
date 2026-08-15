package com.kartikeyajhamnani_017.nexus.order_service.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;

public record OrderRequest(
        @NotBlank(message = "productId must not be blank") String productId,
        @Min(value = 1, message = "quantity must be at least 1") int quantity
) {
}
