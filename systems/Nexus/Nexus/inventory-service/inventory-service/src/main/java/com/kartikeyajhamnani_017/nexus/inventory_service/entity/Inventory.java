package com.kartikeyajhamnani_017.nexus.inventory_service.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.Instant;

@Entity
@Table(name = "inventory", uniqueConstraints = @UniqueConstraint(columnNames = "productId"))
@Getter
@Setter
@NoArgsConstructor
public class Inventory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String productId;

    @Column(nullable = false)
    private int stock;

    @Column(nullable = false)
    private Instant updatedAt = Instant.now();

    public Inventory(String productId, int stock) {
        this.productId = productId;
        this.stock = stock;
        this.updatedAt = Instant.now();
    }
}
