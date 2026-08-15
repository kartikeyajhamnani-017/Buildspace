package com.kartikeyajhamnani_017.nexus.product_service.service;

import com.kartikeyajhamnani_017.nexus.product_service.document.Product;
import com.kartikeyajhamnani_017.nexus.product_service.dto.ProductRequest;
import com.kartikeyajhamnani_017.nexus.product_service.exception.ProductNotFoundException;
import com.kartikeyajhamnani_017.nexus.product_service.repository.ProductRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ProductService {

    private static final Logger log = LoggerFactory.getLogger(ProductService.class);

    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public Product createProduct(ProductRequest request) {
        Product saved = productRepository.save(new Product(request.name(), request.description(), request.price()));
        log.info("product.created productId={} name={}", saved.getId(), saved.getName());
        return saved;
    }

    public List<Product> listProducts() {
        return productRepository.findAll();
    }

    public Product getProduct(String id) {
        return productRepository.findById(id)
                .orElseThrow(() -> new ProductNotFoundException(id));
    }
}
