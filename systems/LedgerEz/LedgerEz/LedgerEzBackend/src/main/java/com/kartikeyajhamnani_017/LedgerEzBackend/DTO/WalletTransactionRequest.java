package com.kartikeyajhamnani_017.LedgerEzBackend.DTO;


import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

/**
 * DTO for handling wallet transactions like "add funds".
 * This is the contract for POST /api/v1/wallet/add
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class WalletTransactionRequest {

    /**
     * The amount to add.
     * @NotNull ensures the field is present.
     * @DecimalMin ensures the amount is positive and greater than zero.
     */
    @NotNull(message = "Amount cannot be null")
    @DecimalMin(value = "0.01", message = "Amount must be greater than zero")
    private BigDecimal amount;
}
