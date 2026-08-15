package com.kartikeyajhamnani_017.Internal_flag_manager.model;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.*; // Make sure to import these
import lombok.Data; // This one annotation replaces all getters/setters/constructors
import org.hibernate.annotations.CreationTimestamp; // For the create date
import java.time.Instant;

@Data // <-- Replaces all getters, setters, toString, and the empty constructor
@Entity
@Table(name = "feature_flag") // <-- Tells Spring to use your 'feature_flag' table
public class Features {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id; // <-- Cleaner name (maps to 'id' column)

    @Column(nullable = false, unique = true) // <-- Matches DB constraints
    private String name; // <-- Cleaner name (maps to 'name' column)

    @Column // Not required, but good practice
    private String description; // <-- Cleaner name (maps to 'description' column)

    @Column(nullable = false) // <-- Matches DB constraints
    private boolean isActive = false; // <-- Correct type! (maps to 'is_active' column)

    @CreationTimestamp // <-- Automatically sets the create time
    @Column(nullable = false, updatable = false)
    private Instant createdAt;

    // You don't need any getters or setters here!
    // Lombok creates them for you.
}
