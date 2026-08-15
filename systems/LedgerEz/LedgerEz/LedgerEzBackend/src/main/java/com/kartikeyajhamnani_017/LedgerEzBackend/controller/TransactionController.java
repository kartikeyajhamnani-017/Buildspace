package com.kartikeyajhamnani_017.LedgerEzBackend.controller;



import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.TransactionRequest;
import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.TransactionResponse;
import com.kartikeyajhamnani_017.LedgerEzBackend.service.PdfGenerationService;
import com.kartikeyajhamnani_017.LedgerEzBackend.service.TransactionService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;

/**
 * REST Controller for handling P2P Transactions.
 */
@RestController
@RequestMapping("/api/v1/transactions")
@RequiredArgsConstructor
public class TransactionController {

    private final TransactionService transactionService;
    private final PdfGenerationService pdfGenerationService;

    /**
     * POST /api/v1/transactions/send
     * <p>
     * Executes a secure P2P funds transfer from the authenticated
     * user to one of their contacts.
     *
     * @param request The DTO containing transfer details.
     * @return A receipt (TransactionResponse) if successful, or
     * a 400/404 error if validation fails.
     */
    @PostMapping("/send")
    public ResponseEntity<?> sendFunds(@Valid @RequestBody TransactionRequest request) {

        Map<String, String> errorBody = new HashMap<>();

        try {
            // --- HAPPY PATH ---
            // We call the service, which does all the work.
            TransactionResponse receipt = transactionService.sendFunds(request);

            // On success, return 200 OK with the receipt
            return ResponseEntity.ok(receipt);

        } catch (NoSuchElementException ex) {
            // --- ERROR PATH 1 (404) ---
            // Catches "User not found" or "Wallet not found"
            errorBody.put("status", "404");
            errorBody.put("error", "Not Found");
            errorBody.put("message", ex.getMessage());
            return new ResponseEntity<>(errorBody, HttpStatus.NOT_FOUND);

        } catch (IllegalArgumentException ex) {
            // --- ERROR PATH 2 (400) ---
            // Catches "Insufficient funds", "Self-send", "Not a contact"
            errorBody.put("status", "400");
            errorBody.put("error", "Bad Request");
            errorBody.put("message", ex.getMessage());
            return new ResponseEntity<>(errorBody, HttpStatus.BAD_REQUEST);
        }
    }

    @GetMapping("/history")
    public ResponseEntity<List<TransactionResponse>> getHistory() {
        return ResponseEntity.ok(transactionService.getTransactionHistory());
    }


    @GetMapping("/statement")
    public ResponseEntity<?> getStatement() { // <-- Change return type to ResponseEntity<?>

        try {
            // --- HAPPY PATH ---
            byte[] pdfBytes = pdfGenerationService.generatePdfStatement();

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_PDF);
            headers.setContentDispositionFormData("attachment", "statement.pdf");
            headers.setContentLength(pdfBytes.length);

            // On success, return the PDF
            return new ResponseEntity<>(pdfBytes, headers, HttpStatus.OK);

        } catch (Exception ex) {
            // --- ERROR PATH ---
            // This will catch *any* error from the PDF service
            // (e.g., TemplateNotFound, ClassNotFound, etc.)

            // Log the real error to the console for debugging
            ex.printStackTrace();

            Map<String, String> errorBody = new HashMap<>();
            errorBody.put("status", "500");
            errorBody.put("error", "Internal Server Error");
            errorBody.put("message", "Could not generate PDF: " + ex.getMessage());

            // Return a clean 500 error, NOT a 403
            return new ResponseEntity<>(errorBody, HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
}