package com.kartikeyajhamnani_017.nexus.inventory_service.repository;

import com.kartikeyajhamnani_017.nexus.inventory_service.entity.Inventory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.Instant;
import java.util.Optional;

public interface InventoryRepository extends JpaRepository<Inventory, Long> {

    Optional<Inventory> findByProductId(String productId);

    boolean existsByProductId(String productId);

    /**
     * Atomically decrements stock only if enough is available, avoiding lost
     * updates from concurrent order events. Returns rows affected: 0 means
     * either the product has no inventory record, or stock was insufficient.
     */
    @Modifying
    @Query("UPDATE Inventory i SET i.stock = i.stock - :qty, i.updatedAt = :now " +
            "WHERE i.productId = :productId AND i.stock >= :qty")
    int decrementStock(@Param("productId") String productId, @Param("qty") int qty, @Param("now") Instant now);
}
