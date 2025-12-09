package com.dreamdemo.inventory.repository;

import com.dreamdemo.inventory.entity.InventoryTransaction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface InventoryTransactionRepository extends JpaRepository<InventoryTransaction, UUID> {

    List<InventoryTransaction> findByProductIdOrderByCreatedAtDesc(Long productId);

    List<InventoryTransaction> findByOrderIdOrderByCreatedAtDesc(String orderId);

    List<InventoryTransaction> findByTransactionTypeOrderByCreatedAtDesc(String transactionType);
}