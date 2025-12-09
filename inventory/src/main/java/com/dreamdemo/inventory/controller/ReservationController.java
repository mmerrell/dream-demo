package com.dreamdemo.inventory.controller;

import com.dreamdemo.inventory.dto.CommitRequest;
import com.dreamdemo.inventory.dto.ReservationRequest;
import com.dreamdemo.inventory.dto.ReservationResponse;
import com.dreamdemo.inventory.dto.RollbackRequest;
import com.dreamdemo.inventory.service.InventoryService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/reserve")
@RequiredArgsConstructor
@Slf4j
public class ReservationController {

    private final InventoryService inventoryService;

    /**
     * POST /reserve
     * Reserve stock for an order.
     *
     * Request:
     * {
     *   "orderId": "order-123",
     *   "productId": 456,
     *   "quantity": 5
     * }
     *
     * Response (success):
     * {
     *   "reservationId": "res-xyz",
     *   "orderId": "order-123",
     *   "productId": 456,
     *   "quantityReserved": 5,
     *   "status": "PENDING",
     *   "createdAt": "2025-12-08T...",
     *   "expiresAt": "2025-12-08T..."
     * }
     *
     * Response (failure):
     * {
     *   "status": "FAILED",
     *   "error": "INSUFFICIENT_STOCK",
     *   "message": "Only 2 available"
     * }
     */
    @PostMapping
    public ResponseEntity<ReservationResponse> reserve(
            @Valid @RequestBody ReservationRequest request
    ) {
        log.info("POST /reserve - Order: {}, Product: {}, Quantity: {}",
                request.getOrderId(), request.getProductId(), request.getQuantity());

        try {
            ReservationResponse response = inventoryService.reserve(request);

            if ("FAILED".equals(response.getStatus())) {
                return ResponseEntity.status(HttpStatus.CONFLICT).body(response);
            }

            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (Exception e) {
            log.error("Error reserving inventory", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ReservationResponse.builder()
                            .status("FAILED")
                            .error("INTERNAL_ERROR")
                            .message(e.getMessage())
                            .build());
        }
    }

    /**
     * POST /reserve/commit
     * Commit a reservation (finalize the order).
     *
     * Request:
     * {
     *   "reservationId": "res-xyz"
     * }
     *
     * Response:
     * {
     *   "reservationId": "res-xyz",
     *   "status": "COMMITTED",
     *   "committedAt": "2025-12-08T..."
     * }
     */
    @PostMapping("/commit")
    public ResponseEntity<ReservationResponse> commit(
            @Valid @RequestBody CommitRequest request
    ) {
        log.info("POST /reserve/commit - Reservation: {}", request.getReservationId());

        try {
            ReservationResponse response = inventoryService.commit(request.getReservationId());
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            log.warn("Invalid reservation ID: {}", request.getReservationId());
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(ReservationResponse.builder()
                            .status("FAILED")
                            .error("RESERVATION_NOT_FOUND")
                            .message(e.getMessage())
                            .build());
        } catch (IllegalStateException e) {
            log.warn("Invalid reservation state: {}", request.getReservationId());
            return ResponseEntity.status(HttpStatus.CONFLICT)
                    .body(ReservationResponse.builder()
                            .status("FAILED")
                            .error("INVALID_STATE")
                            .message(e.getMessage())
                            .build());
        } catch (Exception e) {
            log.error("Error committing reservation", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ReservationResponse.builder()
                            .status("FAILED")
                            .error("INTERNAL_ERROR")
                            .message(e.getMessage())
                            .build());
        }
    }

    /**
     * POST /reserve/rollback
     * Rollback a reservation (cancel the order).
     *
     * Request:
     * {
     *   "reservationId": "res-xyz"
     * }
     *
     * Response:
     * {
     *   "reservationId": "res-xyz",
     *   "status": "ROLLED_BACK",
     *   "rolledBackAt": "2025-12-08T..."
     * }
     */
    @PostMapping("/rollback")
    public ResponseEntity<ReservationResponse> rollback(
            @Valid @RequestBody RollbackRequest request
    ) {
        log.info("POST /reserve/rollback - Reservation: {}", request.getReservationId());

        try {
            ReservationResponse response = inventoryService.rollback(request.getReservationId());
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            log.warn("Invalid reservation ID: {}", request.getReservationId());
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(ReservationResponse.builder()
                            .status("FAILED")
                            .error("RESERVATION_NOT_FOUND")
                            .message(e.getMessage())
                            .build());
        } catch (IllegalStateException e) {
            log.warn("Invalid reservation state: {}", request.getReservationId());
            return ResponseEntity.status(HttpStatus.CONFLICT)
                    .body(ReservationResponse.builder()
                            .status("FAILED")
                            .error("INVALID_STATE")
                            .message(e.getMessage())
                            .build());
        } catch (Exception e) {
            log.error("Error rolling back reservation", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ReservationResponse.builder()
                            .status("FAILED")
                            .error("INTERNAL_ERROR")
                            .message(e.getMessage())
                            .build());
        }
    }
}