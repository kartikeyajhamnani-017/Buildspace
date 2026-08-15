package com.kartikeyajhamnani_017.LedgerEzBackend.model;


import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Represents a contact relationship between two users.
 * This is a one-directional "follow" (User A adds User B).
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "contacts",
        // Add a unique constraint to prevent duplicate entries
        uniqueConstraints = {
                @UniqueConstraint(columnNames = {"owner_user_id", "contact_user_id"})
        })
public class Contact {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer contactId;

    /**
     * The user who "owns" this contact entry (the person who did the adding).
     * This is a Many-to-One relationship.
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "owner_user_id", nullable = false)
    private UserEntity ownerUser;

    /**
     * The user who is "being added" as a contact.
     * This is also a Many-to-One relationship.
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "contact_user_id", nullable = false)
    private UserEntity contactUser;
}