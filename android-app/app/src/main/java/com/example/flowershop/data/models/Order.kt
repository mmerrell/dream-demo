package com.example.flowershop.data.models

import android.os.Parcelable
import kotlinx.parcelize.Parcelize
import java.math.BigDecimal

@Parcelize
data class Order(
    val id: Int,
    val owner_id: Int,
    val created_at: String,
    val status: String,
    val items: List<OrderItem>
) : Parcelable {
    fun getTotalAmount(): BigDecimal {
        return items.fold(BigDecimal.ZERO) { acc, item ->
            acc + (BigDecimal(item.price_at_purchase) * item.quantity.toBigDecimal())
        }
    }
}

@Parcelize
data class OrderItem(
    val id: Int,
    val product_id: Int,
    val quantity: Int,
    val price_at_purchase: String,
    val product: Product
) : Parcelable

data class OrderItemCreate(
    val product_id: Int,
    val quantity: Int
)

data class OrderCreate(
    val items: List<OrderItemCreate>
)

data class PaymentIntentCreateRequest(
    val order_id: Int
)

data class PaymentIntentResponse(
    val client_secret: String
)

