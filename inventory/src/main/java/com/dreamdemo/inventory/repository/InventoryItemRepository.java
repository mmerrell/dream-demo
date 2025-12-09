package com.dreamdemo.inventory.repository;

import com.dreamdemo.inventory.entity.InventoryItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface InventoryItemRepository extends JpaRepository<InventoryItem, UUID> {
    Optional<InventoryItem> findByProductId(Long productId);
    List<InventoryItem> findByProductIdIn(List<Long> productIds);
}