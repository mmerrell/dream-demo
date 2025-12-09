package com.dreamdemo.inventory.dto;

import com.dreamdemo.inventory.entity.InventoryReservation;
import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.ZonedDateTime;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ReservationResponse {
    private UUID reservationId;
    private String orderId;
    private Long productId;
    private Integer quantityReserved;
    private String status;
    private ZonedDateTime createdAt;
    private ZonedDateTime expiresAt;
    private ZonedDateTime committedAt;
    private ZonedDateTime rolledBackAt;

    // For error responses
    private String error;
    private String message;

    public static ReservationResponse fromEntity(InventoryReservation entity) {
        return ReservationResponse.builder()
                .reservationId(entity.getId())
                .orderId(entity.getOrderId())
                .productId(entity.getProductId())
                .quantityReserved(entity.getQuantityReserved())
                .status(entity.getStatus())
                .createdAt(entity.getCreatedAt())
                .expiresAt(entity.getExpiresAt())
                .committedAt(entity.getCommittedAt())
                .rolledBackAt(entity.getRolledBackAt())
                .build();
    }
}