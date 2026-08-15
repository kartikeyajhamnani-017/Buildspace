package com.kartikeyajhamnani_017.LedgerEzBackend.DTO;


import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

/**
 * DTO for sending the user's wallet balance.
 * This is the "contract" for the /api/v1/wallet/balance endpoint.
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class WalletBalanceResponse {
    private String email;
    private BigDecimal balance;
}
