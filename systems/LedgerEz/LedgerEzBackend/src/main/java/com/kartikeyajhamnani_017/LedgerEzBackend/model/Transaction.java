package com.kartikeyajhamnani_017.LedgerEzBackend.model;



import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Represents a single transaction (a "ledger entry") in the system.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "transactions")
public class Transaction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer transactionId;

    /**
     * The user sending the money.
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "from_user_id", nullable = false)
    private UserEntity fromUser;

    /**
     * The user receiving the money.
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "to_user_id", nullable = false)
    private UserEntity toUser;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal amount;

    /**
     * A user-provided description (e.g., "for lunch").
     */
    @Column(nullable = true)
    private String description;

    /**
     * The exact time the transaction was processed.
     */
    @Column(nullable = false)
    private LocalDateTime timestamp;

    /**
     * We can use an Enum to define the status.
     * We will create this Enum in the next step.
     */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TransactionStatus status;

}