package com.kartikeyajhamnani_017.nexus.inventory_service.service;

import com.kartikeyajhamnani_017.nexus.inventory_service.dto.InventoryRequest;
import com.kartikeyajhamnani_017.nexus.inventory_service.entity.Inventory;
import com.kartikeyajhamnani_017.nexus.inventory_service.exception.InventoryAlreadyExistsException;
import com.kartikeyajhamnani_017.nexus.inventory_service.exception.InventoryNotFoundException;
import com.kartikeyajhamnani_017.nexus.inventory_service.repository.InventoryRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;

@Service
public class InventoryService {

    private static final Logger log = LoggerFactory.getLogger(InventoryService.class);

    private final InventoryRepository inventoryRepository;

    public InventoryService(InventoryRepository inventoryRepository) {
        this.inventoryRepository = inventoryRepository;
    }

    @Transactional
    public Inventory seedStock(InventoryRequest request) {
        if (inventoryRepository.existsByProductId(request.productId())) {
            throw new InventoryAlreadyExistsException(request.productId());
        }
        Inventory saved = inventoryRepository.save(new Inventory(request.productId(), request.stock()));
        log.info("inventory.seeded productId={} stock={}", saved.getProductId(), saved.getStock());
        return saved;
    }

    public Inventory getStock(String productId) {
        return inventoryRepository.findByProductId(productId)
                .orElseThrow(() -> new InventoryNotFoundException(productId));
    }

    /**
     * Applies an order event's stock decrement atomically. Returns false if
     * there was no inventory record or stock was insufficient - a business
     * outcome, not an infrastructure failure, so callers should not retry it.
     */
    @Transactional
    public boolean applyOrderDecrement(String productId, int quantity) {
        int updated = inventoryRepository.decrementStock(productId, quantity, Instant.now());
        return updated > 0;
    }
}
