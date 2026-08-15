package com.kartikeyajhamnani_017.LedgerEzBackend.DTO;



import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotEmpty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO for the "Add Contact" request.
 * It contains the email of the user to be added.
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class ContactAddRequest {

    /**
     * The email of the user to add as a contact.
     * We validate that it's not empty and is a valid email format.
     */
    @NotEmpty(message = "Email cannot be empty")
    @Email(message = "Invalid email format")
    private String email;
}
