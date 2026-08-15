package com.kartikeyajhamnani_017.LedgerEzBackend.controller;


import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.AuthenticationResponse;
import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.LoginRequest;
import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.RegisterRequest;
import com.kartikeyajhamnani_017.LedgerEzBackend.service.AuthenticationService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * REST Controller for handling authentication endpoints
 * like user registration and login.
 */
@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthenticationService authService;

    /**
     * Endpoint for registering a new user.
     * @param request The registration request details (firstName, email, password).
     * @return A ResponseEntity containing the JWT token.
     */
    @PostMapping("/register")
    public ResponseEntity<AuthenticationResponse> register(
            @RequestBody RegisterRequest request
    ) {
        return ResponseEntity.ok(authService.register(request));
    }

    /**
     * Endpoint for authenticating an existing user.
     * @param request The login request details (email, password).
     * @return A ResponseEntity containing the JWT token.
     */
    @PostMapping("/login")
    public ResponseEntity<AuthenticationResponse> login(
            @RequestBody LoginRequest request
    ) {
        return ResponseEntity.ok(authService.login(request));
    }
}