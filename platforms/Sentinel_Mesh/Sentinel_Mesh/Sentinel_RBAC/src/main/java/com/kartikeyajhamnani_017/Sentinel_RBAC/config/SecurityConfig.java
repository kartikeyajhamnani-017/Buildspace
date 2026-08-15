package com.kartikeyajhamnani_017.Sentinel_RBAC.config;



import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity // Allows using @PreAuthorize on specific service/controller methods if needed
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                // 1. Route Authorization
                .authorizeHttpRequests(auth -> auth
                        // Allow static assets to load before login
                        .requestMatchers("/css/**", "/js/**", "/img/**").permitAll()

                        // RBAC Rules - Ranked from most restrictive to least restrictive
                        .requestMatchers("/admin/**").hasRole("ADMIN")
                        .requestMatchers("/forensics/**", "/hunt/**").hasAnyRole("ADMIN", "THREAT_HUNTER")
                        .requestMatchers("/api/alerts/*/resolve").hasAnyRole("ADMIN", "SOC_ANALYST")

                        // Everyone including the common VIEWER can access the read-heavy dashboard
                        .requestMatchers("/dashboard/**").hasAnyRole("ADMIN", "THREAT_HUNTER", "SOC_ANALYST", "VIEWER")

                        // Any other request requires at least a login
                        .anyRequest().authenticated()
                )
                // 2. Login Configuration
                .formLogin(form -> form
                        .defaultSuccessUrl("/dashboard", true)
                        .permitAll()
                )
                // 3. Logout Configuration
                .logout(logout -> logout
                        .logoutSuccessUrl("/login?logout")
                        .permitAll()
                );

        return http.build();
    }

    /**
     * IN-MEMORY USERS FOR DEVELOPMENT
     * Replace this later with a database-backed UserDetailsService connecting to PostgreSQL
     */
    @Bean
    public UserDetailsService userDetailsService() {
        UserDetails admin = User.withDefaultPasswordEncoder()
                .username("admin").password("admin123").roles("ADMIN").build();

        UserDetails threatHunter = User.withDefaultPasswordEncoder()
                .username("hunter").password("hunt123").roles("THREAT_HUNTER").build();

        UserDetails socAnalyst = User.withDefaultPasswordEncoder()
                .username("analyst").password("soc123").roles("SOC_ANALYST").build();

        UserDetails viewer = User.withDefaultPasswordEncoder()
                .username("viewer").password("view123").roles("VIEWER").build();

        return new InMemoryUserDetailsManager(admin, threatHunter, socAnalyst, viewer);
    }
}
