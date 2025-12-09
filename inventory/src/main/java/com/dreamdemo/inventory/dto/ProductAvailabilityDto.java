package com.dreamdemo.inventory.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.ZonedDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ProductAvailabilityDto {
    private Long productId;
    private Integer totalAvailable;
    private Integer quantityReserved;
    private Integer quantityDamaged;
    private String status; // IN_STOCK, LOW_STOCK, OUT_OF_STOCK
    private ZonedDateTime asOf;
}
