package com.kartikeyajhamnani_017.LedgerEzBackend.DTO;



import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

/**
 * DTO (Data Contract) for a new P2P transaction.
 * This is the JSON body the React app will send.
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class TransactionRequest {

    @NotEmpty(message = "Receiver email cannot be empty")
    @Email(message = "Invalid email format")
    private String receiverEmail;

    @NotNull(message = "Amount cannot be null")
    @DecimalMin(value = "0.01", message = "Amount must be greater than zero")
    private BigDecimal amount;

    @Size(max = 100, message = "Description can be up to 100 characters")
    private String description; // Optional
}
