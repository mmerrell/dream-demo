package com.dreamdemo.inventory.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.ZonedDateTime;
import java.util.UUID;

@Entity
@Table(name = "inventory_transaction", indexes = {
        @Index(name = "idx_inventory_transaction_product_id", columnList = "product_id"),
        @Index(name = "idx_inventory_transaction_batch_id", columnList = "batch_id"),
        @Index(name = "idx_inventory_transaction_order_id", columnList = "order_id"),
        @Index(name = "idx_inventory_transaction_type", columnList = "transaction_type"),
        @Index(name = "idx_inventory_transaction_created_at", columnList = "created_at")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class InventoryTransaction {

    @Id
    @GeneratedValue
    private UUID id;

    @Column(nullable = false)
    private Long productId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "batch_id")
    private InventoryBatch batch;

    @Column(nullable = false)
    private String transactionType; // RECEIVE, RESERVE, COMMIT, ROLLBACK, DAMAGE, EXPIRE

    @Column(nullable = false)
    private Integer quantityChange;

    @Column
    private String reason;

    @Column
    private String orderId;

    @Column
    private UUID reservationId;

    @Column(nullable = false)
    private ZonedDateTime createdAt;

    @Column
    private String createdBy;

    @PrePersist
    protected void onCreate() {
        createdAt = ZonedDateTime.now();
    }
}