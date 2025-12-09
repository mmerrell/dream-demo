package com.dreamdemo.inventory.repository;

import com.dreamdemo.inventory.entity.InventoryBatch;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface InventoryBatchRepository extends JpaRepository<InventoryBatch, UUID> {

    List<InventoryBatch> findByProductIdAndStatusOrderByExpirationDateAsc(Long productId, String status);

    Optional<InventoryBatch> findByProductIdAndBatchNumber(Long productId, String batchNumber);

    @Query("SELECT b FROM InventoryBatch b WHERE b.productId = :productId AND b.status = 'ACTIVE' " +
            "AND b.quantityAvailable > b.quantityDamaged ORDER BY b.expirationDate ASC")
    List<InventoryBatch> findAvailableBatchesForProduct(@Param("productId") Long productId);

    @Query("SELECT b FROM InventoryBatch b WHERE b.expirationDate < CURRENT_DATE AND b.status = 'ACTIVE'")
    List<InventoryBatch> findExpiredBatches();
}