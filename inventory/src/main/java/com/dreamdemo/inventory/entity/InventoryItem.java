package com.dreamdemo.inventory.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.ZonedDateTime;
import java.util.UUID;

@Entity
@Table(name = "inventory_items", indexes = {
        @Index(name = "idx_inventory_items_product_id", columnList = "product_id")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class InventoryItem {

    @Id
    @GeneratedValue
    private UUID id;

    @Column(nullable = false, unique = true)
    private Long productId;

    @Column(nullable = false)
    private Integer quantityAvailable;

    @Column(nullable = false)
    private Integer quantityReserved;

    @Column(nullable = false)
    private Integer quantityDamaged;

    @Column(nullable = false)
    private ZonedDateTime lastUpdated;

    @Column(nullable = false)
    private ZonedDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = ZonedDateTime.now();
        lastUpdated = ZonedDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        lastUpdated = ZonedDateTime.now();
    }

    public Integer getAvailableForReservation() {
        return quantityAvailable - quantityReserved - quantityDamaged;
    }
}