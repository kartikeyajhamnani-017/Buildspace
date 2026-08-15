package com.kartikeyajhamnani_017.LedgerEzBackend.model;



import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.time.LocalDateTime;
import java.util.Collection;
import java.util.List;

/**
 * Represents the User entity, based on the synopsis schema.
 * This class also implements Spring Security's UserDetails interface
 * to integrate directly with the authentication mechanism.
 */
@Data // Generates getters, setters, toString, equals, and hashCode
@Builder // Provides a builder pattern for object creation
@NoArgsConstructor // Generates a no-argument constructor
@AllArgsConstructor // Generates an all-argument constructor
@Entity // Marks this class as a JPA entity
@Table(name = "users") // Maps this entity to the "users" table
public class UserEntity implements UserDetails {

    /**
     * Primary Key for the User.
     * Corresponds to 'user_id' in the synopsis.
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * User's first name.
     * Corresponds to 'first_name' in the synopsis.
     */
    @Column(name = "first_name", nullable = false)
    private String firstName;

    /**
     * User's email address. Used as the username for login.
     * Corresponds to 'email' in the synopsis.
     */
    @Column(nullable = false, unique = true)
    private String email;

    /**
     * User's hashed password.
     * Corresponds to 'password_hash' in the synopsis.
     */
    @Column(name = "password_hash", nullable = false)
    private String password;

    /**
     * Timestamp of when the user account was created.
     * Corresponds to 'created_at' in the synopsis.
     */
    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @OneToOne(mappedBy = "user", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private WalletEntity wallet;
    // TODO: Add relationships from your synopsis later
    // @OneToOne(mappedBy = "user")
    // private Wallet wallet;
    //
    // @OneToMany(mappedBy = "ownerUser")
    // private List<Contact> contacts;


    // --- UserDetails Interface Methods ---
    // These methods are required by Spring Security

    /**
     * Returns the authorities granted to the user.
     * For now, we'll grant every user a simple "ROLE_USER".
     */
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        // You can expand this later to include roles like "ROLE_ADMIN"
        return List.of(new SimpleGrantedAuthority("ROLE_USER"));
    }

    /**
     * Returns the password used to authenticate the user.
     * This maps to our 'password_hash' field.
     */
    @Override
    public String getPassword() {
        return password;
    }

    /**
     * Returns the username used to authenticate the user.
     * We will use the email as the username.
     */
    @Override
    public String getUsername() {
        return email;
    }



    /**
     * Indicates whether the user's account has expired.
     * We'll default to 'true' (not expired).
     */
    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    /**
     * Indicates whether the user is locked or unlocked.
     * We'll default to 'true' (not locked).
     */
    @Override
    public boolean isAccountNonLocked() {
        return true;
    }

    /**
     * Indicates whether the user's credentials (password) has expired.
     * We'll default to 'true' (not expired).
     */
    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    /**
     * Indicates whether the user is enabled or disabled.
     * We'll default to 'true' (enabled).
     */
    @Override
    public boolean isEnabled() {
        return true;
    }
}
