package com.kartikeyajhamnani_017.LedgerEzBackend.repository;



import com.kartikeyajhamnani_017.LedgerEzBackend.model.Contact;
import com.kartikeyajhamnani_017.LedgerEzBackend.model.UserEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ContactRepository extends JpaRepository<Contact, Integer> {

    /**
     * Returns all contacts owned by a specific user.
     */
    List<Contact> findByOwnerUser(UserEntity ownerUser);

    /**
     * Checks if a contact relationship already exists.
     */
    boolean existsByOwnerUserAndContactUser(
            UserEntity ownerUser,
            UserEntity contactUser
    );
}