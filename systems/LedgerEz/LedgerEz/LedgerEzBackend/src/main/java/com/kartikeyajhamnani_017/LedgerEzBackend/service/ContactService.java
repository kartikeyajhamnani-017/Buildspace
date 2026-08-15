package com.kartikeyajhamnani_017.LedgerEzBackend.service;



import com.kartikeyajhamnani_017.LedgerEzBackend.DTO.ContactAddRequest;
import com.kartikeyajhamnani_017.LedgerEzBackend.model.Contact;
import com.kartikeyajhamnani_017.LedgerEzBackend.model.UserEntity;
import com.kartikeyajhamnani_017.LedgerEzBackend.repository.ContactRepository;
import com.kartikeyajhamnani_017.LedgerEzBackend.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import java.util.NoSuchElementException;

/**
 * Service layer for handling all Contact-related business logic.
 */
@Service
@RequiredArgsConstructor
public class ContactService {

    private final UserRepository userRepository;
    private final ContactRepository contactRepository;

    /**
     * Adds a new contact for the currently authenticated user.
     *
     * @param request The request DTO containing the email of the contact to add.
     */
    public void addContact(ContactAddRequest request) {

        // --- Validation 1: Get the "Owner" ---
        // Get the currently logged-in user securely from the context.
        UserEntity ownerUser = (UserEntity) SecurityContextHolder.getContext().getAuthentication().getPrincipal();

        // --- Validation 2: Find the "Contact" ---
        // Find the user they are trying to add.
        UserEntity contactUser = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new NoSuchElementException("User not found with email: " + request.getEmail()));

        // --- Validation 3: Check for Self-Add ---
        if (ownerUser.getId().equals(contactUser.getId())) {
            throw new IllegalArgumentException("You cannot add yourself as a contact.");
        }

        // --- Validation 4: Check for Duplicates ---
        boolean alreadyExists = contactRepository.existsByOwnerUserAndContactUser(ownerUser, contactUser);
        if (alreadyExists) {
            throw new IllegalArgumentException("This person is already in your contacts.");
        }

        // --- Success: Create and Save ---
        Contact newContact = Contact.builder()
                .ownerUser(ownerUser)
                .contactUser(contactUser)
                .build();

        contactRepository.save(newContact);
    }
}