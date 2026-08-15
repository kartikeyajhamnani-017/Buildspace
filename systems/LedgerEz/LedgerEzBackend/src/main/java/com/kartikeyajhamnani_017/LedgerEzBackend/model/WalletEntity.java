package com.kartikeyajhamnani_017.LedgerEzBackend.model;


import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.math.BigDecimal; // Import the correct type for money

/**
 * Represents the user's digital wallet.
 * Each user has exactly one wallet.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "wallets") // Use plural 'wallets' for table name
public class WalletEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer walletId;

    /**
     * This is the "owning" side of the One-to-One relationship.
     * When this wallet is saved, JPA will look at the 'user' object
     * and store its ID in the 'user_id' column.
     */
    @OneToOne(fetch = FetchType.LAZY) // Lazy fetch is more efficient
    @JoinColumn(name = "user_id", nullable = false, unique = true)
    private UserEntity user;

    /**
     * Using BigDecimal for precise monetary values.
     * We set precision and scale to define the format (e.g., 123456.78).
     */
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal balance;
}