package com.kartikeyajhamnani_017.LedgerEzBackend.repository;

import com.kartikeyajhamnani_017.LedgerEzBackend.model.UserEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<UserEntity, Long> {

    /**
     * Finds a user by their email address.
     * This method is essential for the authentication service (UserDetailsService)
     * to look up users by their username (which is their email).
     *
     * @param email The email address to search for.
     * @return An Optional containing the User if found, or an empty Optional otherwise.
     */
    Optional<UserEntity> findByEmail(String email);

}