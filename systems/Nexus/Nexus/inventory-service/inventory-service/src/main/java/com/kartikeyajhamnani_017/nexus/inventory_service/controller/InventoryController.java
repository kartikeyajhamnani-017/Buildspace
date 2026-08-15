package com.kartikeyajhamnani_017.nexus.inventory_service.controller;

import com.kartikeyajhamnani_017.nexus.inventory_service.dto.InventoryRequest;
import com.kartikeyajhamnani_017.nexus.inventory_service.dto.InventoryResponse;
import com.kartikeyajhamnani_017.nexus.inventory_service.entity.Inventory;
import com.kartikeyajhamnani_017.nexus.inventory_service.service.InventoryService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/inventory")
public class InventoryController {

    private final InventoryService inventoryService;

    public InventoryController(InventoryService inventoryService) {
        this.inventoryService = inventoryService;
    }

    @PostMapping
    public ResponseEntity<InventoryResponse> seedStock(@Valid @RequestBody InventoryRequest request) {
        Inventory inventory = inventoryService.seedStock(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(InventoryResponse.from(inventory));
    }

    @GetMapping("/{productId}")
    public ResponseEntity<InventoryResponse> getStock(@PathVariable String productId) {
        Inventory inventory = inventoryService.getStock(productId);
        return ResponseEntity.ok(InventoryResponse.from(inventory));
    }
}
