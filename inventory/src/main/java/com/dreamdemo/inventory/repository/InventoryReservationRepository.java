package com.dreamdemo.inventory.repository;

import com.dreamdemo.inventory.entity.InventoryReservation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.ZonedDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface InventoryReservationRepository extends JpaRepository<InventoryReservation, UUID> {

    Optional<InventoryReservation> findByOrderId(String orderId);

    List<InventoryReservation> findByProductId(Long productId);

    List<InventoryReservation> findByStatus(String status);

    @Query("SELECT r FROM InventoryReservation r WHERE r.status = 'PENDING' AND r.expiresAt < CURRENT_TIMESTAMP")
    List<InventoryReservation> findExpiredReservations();

    @Query("SELECT COALESCE(SUM(r.quantityReserved), 0) FROM InventoryReservation r " +
            "WHERE r.productId = :productId AND r.status IN ('PENDING', 'COMMITTED')")
    Integer getTotalReservedQuantity(@Param("productId") Long productId);
}