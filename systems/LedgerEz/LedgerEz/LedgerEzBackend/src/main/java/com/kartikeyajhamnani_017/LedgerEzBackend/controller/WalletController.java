package com.kartikeyajhamnani_017.LedgerEzBackend.controller;


import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.WalletBalanceResponse;
import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.WalletTransactionRequest;
import com.kartikeyajhamnani_017.LedgerEzBackend.service.WalletService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST Controller for all Wallet-related operations.
 * All endpoints in this controller are secured and require a valid JWT.
 */
@RestController
@RequestMapping("/api/v1/wallet")
@RequiredArgsConstructor
public class WalletController {

    private final WalletService walletService;

    /**
     * GET /api/v1/wallet/balance
     *
     * Gets the wallet balance for the currently authenticated user.
     *
     * @return A ResponseEntity containing the user's balance.
     */
    @GetMapping("/balance")
    public ResponseEntity<WalletBalanceResponse> getBalance() {
        // We just call the service, which handles all the
        // security logic of finding the *correct* user.
        return ResponseEntity.ok(walletService.getBalance());
    }

    @PostMapping("/add")
    public ResponseEntity<WalletBalanceResponse> addfunds(@RequestBody @Valid WalletTransactionRequest request){
        return ResponseEntity.ok(walletService.addfunds(request));
    }
}