package com.kartikeyajhamnani_017.LedgerEzBackend.repository;



import com.kartikeyajhamnani_017.LedgerEzBackend.model.Transaction;
import com.kartikeyajhamnani_017.LedgerEzBackend.model.UserEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface TransactionRepository extends JpaRepository<Transaction, Integer> {
    // We can add methods here later, like:
    // List<Transaction> findByFromUserOrToUser(User user1, User user2);
    @Query("SELECT t FROM Transaction t WHERE t.fromUser = :user OR t.toUser = :user ORDER BY t.timestamp DESC")
    List<Transaction> findAllByUser(UserEntity user);
}
