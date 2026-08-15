package com.kartikeyajhamnani_017.LedgerEzBackend.service;


import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.AuthenticationResponse;
import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.LoginRequest;
import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.RegisterRequest;
import com.kartikeyajhamnani_017.LedgerEzBackend.model.UserEntity;
import com.kartikeyajhamnani_017.LedgerEzBackend.model.WalletEntity;
import com.kartikeyajhamnani_017.LedgerEzBackend.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;

/**
 * Service layer for handling Authentication logic,
 * such as user registration and login.
 */
@Service
@RequiredArgsConstructor // Automatically injects final fields via constructor
public class AuthenticationService {

    private final UserRepository userRepository;
    private final JwtService jwtService;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;

    /**
     * Registers a new user in the system.
     *
     * @param request The registration request containing user details.
     * @return An AuthResponse containing the JWT token.
     */
    public AuthenticationResponse register(RegisterRequest request) {
        // Check if user already exists
        if (userRepository.findByEmail(request.getEmail()).isPresent()) {
            throw new IllegalArgumentException("User with this email already exists");
        }

        // 4. Using explicit types (no 'var') and correct 'User' class
        UserEntity user = UserEntity.builder()
                .firstName(request.getFirstName())
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .build();

        // 5. The wallet is created and linked
        WalletEntity wallet = WalletEntity.builder()
                .user(user)
                .balance(BigDecimal.ZERO)
                .build();

        user.setWallet(wallet);

        // 6. We save the user (and the wallet cascades)
        userRepository.save(user);

        String jwtToken = jwtService.generateToken(user);
        return AuthenticationResponse.builder()
                .token(jwtToken)
                .build();
    }

    /**
     * Authenticates an existing user.
     *
     * @param request The login request containing email and password.
     * @return An AuthResponse containing the JWT token.
     */
    public AuthenticationResponse login(LoginRequest request) {
        // This line will authenticate the user.
        // It uses the UserDetailsService and PasswordEncoder we provide in AppConfig.
        // If credentials are bad, it throws an AuthenticationException.
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        request.getEmail(),
                        request.getPassword()
                )
        );

        // If authentication is successful, find the user
        UserEntity user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new IllegalArgumentException("User not found after authentication"));

        // Generate and return JWT token
        String jwtToken = jwtService.generateToken(user);
        return AuthenticationResponse.builder()
                .token(jwtToken)
                .build();
    }
}