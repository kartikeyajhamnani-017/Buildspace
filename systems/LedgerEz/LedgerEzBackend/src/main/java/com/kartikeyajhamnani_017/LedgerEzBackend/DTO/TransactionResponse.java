package com.kartikeyajhamnani_017.LedgerEzBackend.DTO;



import com.kartikeyajhamnani_017.LedgerEzBackend.model.TransactionStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * DTO (Data Contract) for sending back a completed
 * transaction receipt.
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class TransactionResponse {

    private Integer transactionId;
    private String fromUserEmail;
    private String toUserEmail;
    private BigDecimal amount;
    private String description;
    private LocalDateTime timestamp;
    private TransactionStatus status;
}
