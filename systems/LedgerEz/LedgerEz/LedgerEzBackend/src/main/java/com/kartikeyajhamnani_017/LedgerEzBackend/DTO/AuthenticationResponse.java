package com.kartikeyajhamnani_017.LedgerEzBackend.DTO;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO (Data Transfer Object) for sending back a JWT token
 * upon successful registration or login.
 *
 * This class should ONLY contain data fields.
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class AuthenticationResponse {

    private String token;
    // All the business logic has been removed from this file.
}