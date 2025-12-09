package com.dreamdemo.inventory.service;

import com.dreamdemo.inventory.dto.ProductAvailabilityDto;
import com.dreamdemo.inventory.entity.InventoryItem;
import com.dreamdemo.inventory.repository.InventoryBatchRepository;
import com.dreamdemo.inventory.repository.InventoryItemRepository;
import com.dreamdemo.inventory.repository.InventoryReservationRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.ZonedDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class AvailabilityService {

    private final InventoryItemRepository inventoryItemRepository;
    private final InventoryReservationRepository reservationRepository;
    private final InventoryBatchRepository batchRepository;

    /**
     * Get availability for a list of products.
     * Returns current stock levels, reservations, and availability status.
     */
    @Transactional(readOnly = true)
    public List<ProductAvailabilityDto> getAvailability(List<Long> productIds) {
        log.debug("Getting availability for products: {}", productIds);

        return productIds.stream()
                .map(this::getProductAvailability)
                .collect(Collectors.toList());
    }

    /**
     * Get availability for a single product.
     */
    @Transactional(readOnly = true)
    public ProductAvailabilityDto getProductAvailability(Long productId) {
        InventoryItem item = inventoryItemRepository.findByProductId(productId)
                .orElse(null);

        if (item == null) {
            // Product not in inventory system yet
            return ProductAvailabilityDto.builder()
                    .productId(productId)
                    .totalAvailable(0)
                    .status("OUT_OF_STOCK")
                    .asOf(ZonedDateTime.now())
                    .build();
        }

        int available = item.getAvailableForReservation();
        String status = determineStatus(available);

        return ProductAvailabilityDto.builder()
                .productId(productId)
                .totalAvailable(available)
                .quantityReserved(item.getQuantityReserved())
                .quantityDamaged(item.getQuantityDamaged())
                .status(status)
                .asOf(item.getLastUpdated())
                .build();
    }

    /**
     * Determine availability status based on quantity.
     */
    private String determineStatus(int available) {
        if (available > 10) {
            return "IN_STOCK";
        } else if (available > 0) {
            return "LOW_STOCK";
        } else {
            return "OUT_OF_STOCK";
        }
    }
}