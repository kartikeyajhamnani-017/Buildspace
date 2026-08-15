package com.kartikeyajhamnani_017.LedgerEzBackend.service;


import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.WalletBalanceResponse;
import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.WalletTransactionRequest;
import com.kartikeyajhamnani_017.LedgerEzBackend.model.UserEntity;
import com.kartikeyajhamnani_017.LedgerEzBackend.model.WalletEntity;
import com.kartikeyajhamnani_017.LedgerEzBackend.repository.WalletRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.NoSuchElementException;

/**
 * Contains all business logic for wallet operations.
 */
@Service
@RequiredArgsConstructor
public class WalletService {

    private final WalletRepository walletRepository;

    /**
     * Gets the balance for the *currently authenticated* user.
     *
     * @return A DTO containing the user's email and balance.
     */
    public WalletBalanceResponse getBalance() {
        // 1. Get the authenticated user from the security context
        // This is the secure way to identify the user.
        UserEntity currentUser = (UserEntity) SecurityContextHolder.getContext().getAuthentication().getPrincipal();

        // 2. Find the wallet associated with this user
        WalletEntity wallet = walletRepository.findByUser(currentUser)
                .orElseThrow(() -> new NoSuchElementException("Wallet not found for user: " + currentUser.getEmail()));

        // 3. Build the DTO and return it
        return WalletBalanceResponse.builder()
                .email(currentUser.getEmail())
                .balance(wallet.getBalance())
                .build();
    }

    @Transactional
    public WalletBalanceResponse addfunds(WalletTransactionRequest request){
        // 1. Get the authenticated user from the security context
        // This is the secure way to identify the user.
        UserEntity currentUser = (UserEntity) SecurityContextHolder.getContext().getAuthentication().getPrincipal();

        // 2. Find the wallet associated with this user
        WalletEntity wallet = walletRepository.findAndLockByUser(currentUser)
                .orElseThrow(() -> new NoSuchElementException("Wallet not found for user: " + currentUser.getEmail()));


        BigDecimal newbalance = wallet.getBalance().add(request.getAmount());
        wallet.setBalance(newbalance);
        walletRepository.save(wallet);

        return  WalletBalanceResponse.builder()
                .email(currentUser.getEmail())
                .balance(newbalance)
                .build(); }


}
