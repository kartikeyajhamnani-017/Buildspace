package com.kartikeyajhamnani_017.LedgerEzBackend.service;



import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.WalletBalanceResponse;
import com.kartikeyajhamnani_017.LedgerEzBackend.model.Transaction;
import com.kartikeyajhamnani_017.LedgerEzBackend.model.UserEntity;

import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.thymeleaf.TemplateEngine;
import org.thymeleaf.context.Context;
import org.xhtmlrenderer.pdf.ITextRenderer;

import java.io.ByteArrayOutputStream;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * Service to generate a PDF statement by rendering
 * a Thymeleaf HTML template.
 */
@Service
public class PdfGenerationService {

    private final TemplateEngine templateEngine;
    private final TransactionService transactionService;
    private final WalletService walletService;

    // We inject the beans we need
    public PdfGenerationService(TemplateEngine templateEngine,
                                TransactionService transactionService,
                                WalletService walletService) {
        this.templateEngine = templateEngine;
        this.transactionService = transactionService;
        this.walletService = walletService;
    }

    /**
     * Generates a PDF statement for the current user.
     * @return The PDF file as a byte array.
     */
    public byte[] generatePdfStatement() {
        // 1. Get all the data
        UserEntity currentUser = (UserEntity) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        List<?> transactions = transactionService.getTransactionHistory(); // It's a List<TransactionResponse>
        WalletBalanceResponse balance = walletService.getBalance();

        // 2. Create the Thymeleaf "Context" (the data map)
        Context context = new Context();
        context.setVariables(Map.of(
                "user", currentUser,
                "transactions", transactions,
                "balance", balance,
                "statementDate", LocalDateTime.now()
        ));

        // 3. Render the HTML string from the template
        String html = templateEngine.process("statement-template.html", context);

        // 4. Convert the HTML string to a PDF
        return htmlToPdf(html);
    }

    /**
     * Uses the OpenPDF library (ITextRenderer) to convert
     * an HTML string into a PDF byte array.
     */
    private byte[] htmlToPdf(String html) {
        try (ByteArrayOutputStream outputStream = new ByteArrayOutputStream()) {
            ITextRenderer renderer = new ITextRenderer();

            // --- THIS IS THE FIX ---
            // We have REMOVED the broken addFont() line.
            // --- END OF FIX ---

            renderer.setDocumentFromString(html);
            renderer.layout();
            renderer.createPDF(outputStream);

            return outputStream.toByteArray();
        } catch (Exception e) {
            // In a real app, you'd have better error handling
            e.printStackTrace();
            throw new RuntimeException("Error generating PDF: " + e.getMessage(), e);
        }
    }
}