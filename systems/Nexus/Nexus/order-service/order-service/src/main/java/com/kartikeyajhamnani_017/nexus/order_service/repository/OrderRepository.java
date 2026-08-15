package com.kartikeyajhamnani_017.nexus.order_service.repository;

import com.kartikeyajhamnani_017.nexus.order_service.entity.Order;
import org.springframework.data.jpa.repository.JpaRepository;

public interface OrderRepository extends JpaRepository<Order, Long> {
}
