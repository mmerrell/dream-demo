package com.dreamdemo.inventory.controller;

import com.dreamdemo.inventory.dto.AvailabilityRequest;
import com.dreamdemo.inventory.dto.AvailabilityResponse;
import com.dreamdemo.inventory.dto.ProductAvailabilityDto;
import com.dreamdemo.inventory.service.AvailabilityService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/availability")
@RequiredArgsConstructor
@Slf4j
public class AvailabilityController {

    private final AvailabilityService availabilityService;

    /**
     * GET /availability?product_ids=1,2,3
     * Query availability for one or more products.
     */
    @GetMapping
    public ResponseEntity<AvailabilityResponse> getAvailability(
            @RequestParam("product_ids") List<Long> productIds
    ) {
        log.debug("GET /availability for products: {}", productIds);

        List<ProductAvailabilityDto> availability = availabilityService.getAvailability(productIds);

        return ResponseEntity.ok(AvailabilityResponse.builder()
                .products(availability)
                .build());
    }

    /**
     * GET /availability/{productId}
     * Query availability for a single product.
     */
    @GetMapping("/{productId}")
    public ResponseEntity<ProductAvailabilityDto> getProductAvailability(
            @PathVariable Long productId
    ) {
        log.debug("GET /availability/{}", productId);

        ProductAvailabilityDto availability = availabilityService.getProductAvailability(productId);

        return ResponseEntity.ok(availability);
    }
}