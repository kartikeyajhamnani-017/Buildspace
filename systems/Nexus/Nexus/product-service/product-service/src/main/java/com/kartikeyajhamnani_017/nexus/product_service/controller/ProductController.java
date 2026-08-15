package com.kartikeyajhamnani_017.nexus.product_service.controller;

import com.kartikeyajhamnani_017.nexus.product_service.document.Product;
import com.kartikeyajhamnani_017.nexus.product_service.dto.ProductRequest;
import com.kartikeyajhamnani_017.nexus.product_service.dto.ProductResponse;
import com.kartikeyajhamnani_017.nexus.product_service.service.ProductService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @PostMapping
    public ResponseEntity<ProductResponse> createProduct(@Valid @RequestBody ProductRequest request) {
        Product product = productService.createProduct(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(ProductResponse.from(product));
    }

    @GetMapping
    public ResponseEntity<List<ProductResponse>> listProducts() {
        List<ProductResponse> products = productService.listProducts().stream()
                .map(ProductResponse::from)
                .toList();
        return ResponseEntity.ok(products);
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProductResponse> getProduct(@PathVariable String id) {
        Product product = productService.getProduct(id);
        return ResponseEntity.ok(ProductResponse.from(product));
    }
}
