package com.dreamdemo.inventory.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.ZonedDateTime;
import java.util.UUID;

@Entity
@Table(name = "inventory_reservation", indexes = {
        @Index(name = "idx_inventory_reservation_order_id", columnList = "order_id"),
        @Index(name = "idx_inventory_reservation_product_id", columnList = "product_id"),
        @Index(name = "idx_inventory_reservation_batch_id", columnList = "batch_id"),
        @Index(name = "idx_inventory_reservation_status", columnList = "status"),
        @Index(name = "idx_inventory_reservation_expires_at", columnList = "expires_at")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class InventoryReservation {

    @Id
    @GeneratedValue
    private UUID id;

    @Column(nullable = false, unique = true)
    private String orderId;

    @Column(nullable = false)
    private Long productId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "batch_id", nullable = false)
    private InventoryBatch batch;

    @Column(nullable = false)
    private Integer quantityReserved;

    @Column(nullable = false)
    private String status; // PENDING, COMMITTED, ROLLED_BACK, EXPIRED

    @Column(nullable = false)
    private ZonedDateTime createdAt;

    @Column(nullable = false)
    private ZonedDateTime expiresAt;

    @Column
    private ZonedDateTime committedAt;

    @Column
    private ZonedDateTime rolledBackAt;

    @PrePersist
    protected void onCreate() {
        createdAt = ZonedDateTime.now();
        if (status == null) {
            status = "PENDING";
        }
        if (expiresAt == null) {
            // Default 15 minute reservation window
            expiresAt = ZonedDateTime.now().plusMinutes(15);
        }
    }

    public boolean isExpired() {
        return ZonedDateTime.now().isAfter(expiresAt);
    }

    public boolean isPending() {
        return "PENDING".equals(status);
    }

    public boolean isCommitted() {
        return "COMMITTED".equals(status);
    }

    public boolean isRolledBack() {
        return "ROLLED_BACK".equals(status);
    }
}