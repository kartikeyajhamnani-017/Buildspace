package com.kartikeyajhamnani_017.nexus.inventory_service.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;

public record InventoryRequest(
        @NotBlank(message = "productId must not be blank") String productId,
        @Min(value = 0, message = "stock must not be negative") int stock
) {
}
