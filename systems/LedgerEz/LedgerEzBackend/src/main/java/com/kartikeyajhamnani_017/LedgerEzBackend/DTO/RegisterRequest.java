package com.kartikeyajhamnani_017.LedgerEzBackend.DTO;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO (Data Transfer Object) for handling user registration requests.
 * This object will be created from the JSON body of a POST request.
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class RegisterRequest {
    private String firstName;
    private String email;
    private String password;}
