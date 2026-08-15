package com.kartikeyajhamnani_017.LedgerEzBackend.model;



/**
 * Represents the status of a transaction.
 * For now, we only care if it's COMPLETED, but we can add
 * PENDING or FAILED later for scalability.
 */
public enum TransactionStatus {
    COMPLETED,
    PENDING,
    FAILED
}
