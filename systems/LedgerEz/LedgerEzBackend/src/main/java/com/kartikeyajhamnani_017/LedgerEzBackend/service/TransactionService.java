package com.kartikeyajhamnani_017.LedgerEzBackend.service;



import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.TransactionRequest;
import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.TransactionResponse;
import com.kartikeyajhamnani_017.LedgerEzBackend.model.*; // Import all models
import com.kartikeyajhamnani_017.LedgerEzBackend.repository.ContactRepository;
import com.kartikeyajhamnani_017.LedgerEzBackend.repository.TransactionRepository;
import com.kartikeyajhamnani_017.LedgerEzBackend.repository.UserRepository;
import com.kartikeyajhamnani_017.LedgerEzBackend.repository.WalletRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.stream.Collectors;

/**
 * Service for handling the core P2P ledger transactions.
 */
@Service
@RequiredArgsConstructor
public class TransactionService {

    // We need all 4 repositories to make this work
    private final WalletRepository walletRepository;
    private final UserRepository userRepository;
    private final ContactRepository contactRepository;
    private final TransactionRepository transactionRepository;

    /**
     * Executes a secure, atomic P2P money transfer.
     *
     * @Transactional ensures this is an "all-or-nothing" operation.
     * If any part fails, the entire transaction is rolled back.
     *
     * @param request The DTO containing transfer details.
     * @return A receipt of the completed transaction.
     */
    @Transactional
    public TransactionResponse sendFunds(TransactionRequest request) {

        // --- 1. Get Sender (from security) ---
        UserEntity sender = (UserEntity) SecurityContextHolder.getContext().getAuthentication().getPrincipal();

        // --- 2. Get Receiver (from DTO) ---
        UserEntity receiver = userRepository.findByEmail(request.getReceiverEmail())
                .orElseThrow(() -> new NoSuchElementException("User not found: " + request.getReceiverEmail()));

        // --- 3. Validation (Sanity Checks) ---
        if (sender.getId().equals(receiver.getId())) {
            throw new IllegalArgumentException("You cannot send money to yourself.");
        }

        // This fulfills the synopsis: "track... transactions with their contacts."
        boolean isContact = contactRepository.existsByOwnerUserAndContactUser(sender, receiver);
        if (!isContact) {
            // In a real app, you might also check if the *receiver* has added the *sender*.
            // For now, we enforce a one-way "must be in your contact list" rule.
            throw new IllegalArgumentException("You can only send money to people in your contact list.");
        }

        // --- 4. Validation (Financial) & Locking ---

        // Lock BOTH wallets to prevent any race conditions
        WalletEntity senderWallet = walletRepository.findAndLockByUser(sender)
                .orElseThrow(() -> new NoSuchElementException("Sender wallet not found."));

        WalletEntity receiverWallet = walletRepository.findAndLockByUser(receiver)
                .orElseThrow(() -> new NoSuchElementException("Receiver wallet not found."));

        // Check for sufficient funds
        if (senderWallet.getBalance().compareTo(request.getAmount()) < 0) {
            // compareTo < 0 means (balance < amount)
            throw new IllegalArgumentException("Insufficient funds.");
        }

        // --- 5. Execute (The Atomic Transaction) ---

        // Step 5a: Debit the Sender
        BigDecimal senderNewBalance = senderWallet.getBalance().subtract(request.getAmount());
        senderWallet.setBalance(senderNewBalance);
        walletRepository.save(senderWallet);

        // Step 5b: Credit the Receiver
        BigDecimal receiverNewBalance = receiverWallet.getBalance().add(request.getAmount());
        receiverWallet.setBalance(receiverNewBalance);
        walletRepository.save(receiverWallet);

        // Step 5c: Log the Transaction
        Transaction transactionLog = Transaction.builder()
                .fromUser(sender)
                .toUser(receiver)
                .amount(request.getAmount())
                .description(request.getDescription())
                .timestamp(LocalDateTime.now())
                .status(TransactionStatus.COMPLETED)
                .build();

        Transaction savedLog = transactionRepository.save(transactionLog);

        // --- 6. Return Receipt ---
        return TransactionResponse.builder()
                .transactionId(savedLog.getTransactionId())
                .fromUserEmail(sender.getEmail())
                .toUserEmail(receiver.getEmail())
                .amount(savedLog.getAmount())
                .description(savedLog.getDescription())
                .timestamp(savedLog.getTimestamp())
                .status(savedLog.getStatus())
                .build();
    }

    public List<TransactionResponse> getTransactionHistory() {
        // 1. Get the authenticated user
        UserEntity currentUser = (UserEntity) SecurityContextHolder.getContext().getAuthentication().getPrincipal();

        // 2. Call our new repository method
        List<Transaction> transactions = transactionRepository.findAllByUser(currentUser);

        // 3. Convert the list of 'Transaction' entities into a list of 'TransactionResponse' DTOs
        return transactions.stream()
                .map(this::mapTransactionToResponse) // Use a helper method
                .collect(Collectors.toList());
    }

    /**
     * Private helper method to map a Transaction entity to its DTO.
     * This avoids code duplication.
     */
    private TransactionResponse mapTransactionToResponse(Transaction transaction) {
        return TransactionResponse.builder()
                .transactionId(transaction.getTransactionId())
                .fromUserEmail(transaction.getFromUser().getEmail())
                .toUserEmail(transaction.getToUser().getEmail())
                .amount(transaction.getAmount())
                .description(transaction.getDescription())
                .timestamp(transaction.getTimestamp())
                .status(transaction.getStatus())
                .build();
    }
}