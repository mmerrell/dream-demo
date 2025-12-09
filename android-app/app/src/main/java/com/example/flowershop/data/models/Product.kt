package com.example.flowershop.data.models

import android.os.Parcelable
import kotlinx.parcelize.Parcelize
import java.math.BigDecimal

@Parcelize
data class Product(
    val id: Int,
    val name: String,
    val description: String?,
    val price: String,
    val inventory_count: Int,
    val created_at: String
) : Parcelable {
    fun getPriceDecimal(): BigDecimal = BigDecimal(price)
}

data class ProductCreate(
    val name: String,
    val description: String?,
    val price: String,
    val inventory_count: Int
)

