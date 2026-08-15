package com.kartikeyajhamnani_017.nexus.product_service.repository;

import com.kartikeyajhamnani_017.nexus.product_service.document.Product;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface ProductRepository extends MongoRepository<Product, String> {
}
