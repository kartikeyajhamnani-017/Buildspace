package com.kartikeyajhamnani_017.LedgerEzBackend.controller;

import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.ContactAddRequest;
import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.ContactResponse;
import com.kartikeyajhamnani_017.LedgerEzBackend.model.Contact;
import com.kartikeyajhamnani_017.LedgerEzBackend.model.UserEntity;
import com.kartikeyajhamnani_017.LedgerEzBackend.repository.ContactRepository;
import com.kartikeyajhamnani_017.LedgerEzBackend.repository.UserRepository;
import com.kartikeyajhamnani_017.LedgerEzBackend.service.ContactService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus; // Make sure this is imported
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

// Import these 3 classes for the fix
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;

/**
 * REST Controller for all Contact-related operations.
 * All endpoints are secure.
 */
@RestController
@RequestMapping("/api/v1/contacts")
@RequiredArgsConstructor
public class ContactController {

    private final ContactService contactService;

    /**
     * POST /api/v1/contacts/add
     *
     * This method now includes the MANDATORY try-catch block
     * to correctly handle errors and return 400/404.
     *
     * @param request The request body containing the email of the user to add.
     * @return A 200 OK response if successful, or a 4xx error on failure.
     */
    @PostMapping("/add")
    public ResponseEntity<?> addContact(@Valid @RequestBody ContactAddRequest request) {

        // This Map will hold our clean JSON error
        Map<String, String> errorBody = new HashMap<>();

        try {
            // --- HAPPY PATH ---
            // The service is called. If it succeeds, we're done.
            contactService.addContact(request);

            // Return 200 OK with no body
            return ResponseEntity.ok().build();

        } catch (NoSuchElementException ex) {
            // --- ERROR PATH 1 ---
            // This catches the "User Not Found" exception
            errorBody.put("status", "404");
            errorBody.put("error", "Not Found");
            errorBody.put("message", ex.getMessage());
            return new ResponseEntity<>(errorBody, HttpStatus.NOT_FOUND); // Returns 404

        } catch (IllegalArgumentException ex) {
            // --- ERROR PATH 2 ---
            // This catches "Self-Add" and "Duplicate"
            errorBody.put("status", "400");
            errorBody.put("error", "Bad Request");
            errorBody.put("message", ex.getMessage());
            return new ResponseEntity<>(errorBody, HttpStatus.BAD_REQUEST); // Returns 400
        }
    }

    private final ContactRepository contactRepository;
    private final UserRepository userRepository;

    @GetMapping("/getcontacts")
    public List<ContactResponse> getMyContacts(Authentication authentication) {

        String email = authentication.getName();

        UserEntity owner = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        List<Contact> contacts = contactRepository.findByOwnerUser(owner);

        return contacts.stream()
                .map(contact -> new ContactResponse(
                        contact.getContactId(),
                        contact.getContactUser().getFirstName(),
                        contact.getContactUser().getEmail()
                ))
                .toList();
    }
}