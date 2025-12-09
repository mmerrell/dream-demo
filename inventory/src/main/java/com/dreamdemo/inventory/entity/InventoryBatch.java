package com.dreamdemo.inventory.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDate;
import java.time.ZonedDateTime;
import java.util.UUID;

@Entity
@Table(name = "inventory_batch", indexes = {
        @Index(name = "idx_inventory_batch_product_id", columnList = "product_id"),
        @Index(name = "idx_inventory_batch_status", columnList = "status"),
        @Index(name = "idx_inventory_batch_expiration", columnList = "expiration_date")
}, uniqueConstraints = {
        @UniqueConstraint(columnNames = {"product_id", "batch_number"})
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class InventoryBatch {

    @Id
    @GeneratedValue
    private UUID id;

    @Column(nullable = false)
    private Long productId;

    @Column(nullable = false)
    private String batchNumber;

    @Column(nullable = false)
    private Integer quantityReceived;

    @Column(nullable = false)
    private ZonedDateTime dateReceived;

    @Column(nullable = false)
    private LocalDate expirationDate;

    @Column(nullable = false)
    private Integer quantityAvailable;

    @Column(nullable = false)
    private Integer quantityDamaged;

    @Column(nullable = false)
    private String status; // ACTIVE, EXPIRED, DISCARDED

    @Column(nullable = false)
    private ZonedDateTime createdAt;

    @Column(nullable = false)
    private ZonedDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = ZonedDateTime.now();
        updatedAt = ZonedDateTime.now();
        if (status == null) {
            status = "ACTIVE";
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = ZonedDateTime.now();
    }

    public boolean isExpired() {
        return LocalDate.now().isAfter(expirationDate);
    }

    public Integer getAvailableForReservation() {
        return quantityAvailable - quantityDamaged;
    }
}