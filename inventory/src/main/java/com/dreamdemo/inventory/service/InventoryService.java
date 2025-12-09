package com.dreamdemo.inventory.service;

import com.dreamdemo.inventory.dto.ReservationRequest;
import com.dreamdemo.inventory.dto.ReservationResponse;
import com.dreamdemo.inventory.entity.InventoryBatch;
import com.dreamdemo.inventory.entity.InventoryItem;
import com.dreamdemo.inventory.entity.InventoryReservation;
import com.dreamdemo.inventory.entity.InventoryTransaction;
import com.dreamdemo.inventory.repository.InventoryBatchRepository;
import com.dreamdemo.inventory.repository.InventoryItemRepository;
import com.dreamdemo.inventory.repository.InventoryReservationRepository;
import com.dreamdemo.inventory.repository.InventoryTransactionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.ZonedDateTime;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class InventoryService {

    private final InventoryItemRepository inventoryItemRepository;
    private final InventoryBatchRepository batchRepository;
    private final InventoryReservationRepository reservationRepository;
    private final InventoryTransactionRepository transactionRepository;

    /**
     * Reserve stock for an order.
     * This is an idempotent operation - if the order already has a reservation, return it.
     */
    @Transactional
    public ReservationResponse reserve(ReservationRequest request) {
        log.info("Processing reservation for order: {}, product: {}, quantity: {}",
                request.getOrderId(), request.getProductId(), request.getQuantity());

        // Check if this order already has a reservation
        Optional<InventoryReservation> existingReservation = reservationRepository.findByOrderId(request.getOrderId());
        if (existingReservation.isPresent()) {
            log.info("Reservation already exists for order: {}", request.getOrderId());
            return ReservationResponse.fromEntity(existingReservation.get());
        }

        // Get or create inventory item
        InventoryItem item = inventoryItemRepository.findByProductId(request.getProductId())
                .orElseGet(() -> {
                    InventoryItem newItem = InventoryItem.builder()
                            .productId(request.getProductId())
                            .quantityAvailable(0)
                            .quantityReserved(0)
                            .quantityDamaged(0)
                            .build();
                    return inventoryItemRepository.save(newItem);
                });

        // Find available batches (FIFO by expiration date)
        List<InventoryBatch> availableBatches = batchRepository.findAvailableBatchesForProduct(request.getProductId());

        if (availableBatches.isEmpty()) {
            log.warn("No available batches for product: {}", request.getProductId());
            return ReservationResponse.builder()
                    .status("FAILED")
                    .error("INSUFFICIENT_STOCK")
                    .message("No stock available")
                    .build();
        }

        // Reserve from the first available batch (earliest expiration = FIFO)
        InventoryBatch selectedBatch = availableBatches.get(0);
        int availableInBatch = selectedBatch.getAvailableForReservation();

        if (availableInBatch < request.getQuantity()) {
            log.warn("Insufficient stock in batch. Available: {}, Requested: {}",
                    availableInBatch, request.getQuantity());
            return ReservationResponse.builder()
                    .status("FAILED")
                    .error("INSUFFICIENT_STOCK")
                    .message(String.format("Only %d available", availableInBatch))
                    .build();
        }

        // Create reservation
        InventoryReservation reservation = InventoryReservation.builder()
                .orderId(request.getOrderId())
                .productId(request.getProductId())
                .batch(selectedBatch)
                .quantityReserved(request.getQuantity())
                .status("PENDING")
                .build();

        reservation = reservationRepository.save(reservation);

        // Update inventory item
        item.setQuantityReserved(item.getQuantityReserved() + request.getQuantity());
        item.setLastUpdated(ZonedDateTime.now());
        inventoryItemRepository.save(item);

        // Record transaction
        recordTransaction(
                request.getProductId(),
                selectedBatch,
                "RESERVE",
                request.getQuantity(),
                "Order reservation",
                request.getOrderId(),
                reservation.getId()
        );

        log.info("Reservation created: {} for order: {}", reservation.getId(), request.getOrderId());
        return ReservationResponse.fromEntity(reservation);
    }

    /**
     * Commit a reservation (finalize the order).
     */
    @Transactional
    public ReservationResponse commit(String reservationId) {
        log.info("Committing reservation: {}", reservationId);

        InventoryReservation reservation = reservationRepository.findById(java.util.UUID.fromString(reservationId))
                .orElseThrow(() -> new IllegalArgumentException("Reservation not found: " + reservationId));

        if (!reservation.isPending()) {
            throw new IllegalStateException(
                    String.format("Reservation is not pending. Current status: %s", reservation.getStatus())
            );
        }

        // Fetch the inventory item
        InventoryItem item = inventoryItemRepository.findByProductId(reservation.getProductId())
                .orElseThrow(() -> new IllegalStateException("Inventory item not found"));

        // Update reservation status
        reservation.setStatus("COMMITTED");
        reservation.setCommittedAt(ZonedDateTime.now());
        reservationRepository.save(reservation);

        // Update batch
        InventoryBatch batch = reservation.getBatch();
        batch.setQuantityAvailable(batch.getQuantityAvailable() - reservation.getQuantityReserved());
        batchRepository.save(batch);

        // Update inventory item lastUpdated
        item.setLastUpdated(ZonedDateTime.now());
        inventoryItemRepository.save(item);

        // Record transaction
        recordTransaction(
                reservation.getProductId(),
                batch,
                "COMMIT",
                reservation.getQuantityReserved(),
                "Order committed",
                reservation.getOrderId(),
                reservation.getId()
        );

        log.info("Reservation committed: {}", reservationId);
        return ReservationResponse.fromEntity(reservation);
    }

    /**
     * Rollback a reservation (cancel the order).
     */
    @Transactional
    public ReservationResponse rollback(String reservationId) {
        log.info("Rolling back reservation: {}", reservationId);

        InventoryReservation reservation = reservationRepository.findById(java.util.UUID.fromString(reservationId))
                .orElseThrow(() -> new IllegalArgumentException("Reservation not found: " + reservationId));

        if (!reservation.isPending()) {
            throw new IllegalStateException(
                    String.format("Only pending reservations can be rolled back. Current status: %s", reservation.getStatus())
            );
        }

        // Update reservation status
        reservation.setStatus("ROLLED_BACK");
        reservation.setRolledBackAt(ZonedDateTime.now());
        reservationRepository.save(reservation);

        // Release from inventory item
        InventoryItem item = inventoryItemRepository.findByProductId(reservation.getProductId())
                .orElseThrow(() -> new IllegalStateException("Inventory item not found"));

        item.setQuantityReserved(item.getQuantityReserved() - reservation.getQuantityReserved());
        item.setLastUpdated(ZonedDateTime.now());
        inventoryItemRepository.save(item);

        // Record transaction
        recordTransaction(
                reservation.getProductId(),
                reservation.getBatch(),
                "ROLLBACK",
                -reservation.getQuantityReserved(),
                "Order cancelled/failed",
                reservation.getOrderId(),
                reservation.getId()
        );

        log.info("Reservation rolled back: {}", reservationId);
        return ReservationResponse.fromEntity(reservation);
    }

    /**
     * Helper method to record inventory transactions.
     */
    private void recordTransaction(
            Long productId,
            InventoryBatch batch,
            String transactionType,
            Integer quantityChange,
            String reason,
            String orderId,
            java.util.UUID reservationId
    ) {
        InventoryTransaction transaction = InventoryTransaction.builder()
                .productId(productId)
                .batch(batch)
                .transactionType(transactionType)
                .quantityChange(quantityChange)
                .reason(reason)
                .orderId(orderId)
                .reservationId(reservationId)
                .createdBy("inventory-service")
                .build();

        transactionRepository.save(transaction);
    }
}