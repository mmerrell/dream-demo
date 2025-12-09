package com.example.flowershop.data.api

import com.example.flowershop.data.models.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    
    // Authentication
    @POST("token")
    @FormUrlEncoded
    suspend fun login(
        @Field("username") email: String,
        @Field("password") password: String
    ): Token
    
    @POST("users/")
    suspend fun register(@Body user: UserCreate): User
    
    @GET("users/me/")
    suspend fun getCurrentUser(): User
    
    // Products
    @GET("products/")
    suspend fun getProducts(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 100
    ): List<Product>
    
    @POST("products/")
    suspend fun createProduct(@Body product: ProductCreate): Product
    
    // Orders
    @POST("orders/")
    suspend fun createOrder(@Body order: OrderCreate): Order
    
    @GET("orders/")
    suspend fun getOrders(): List<Order>
    
    @POST("orders/{order_id}/cancel")
    suspend fun cancelOrder(@Path("order_id") orderId: Int): Order
    
    @POST("orders/{order_id}/process-payment")
    suspend fun processPayment(@Path("order_id") orderId: Int): Response<Any>
    
    // Payment
    @POST("create-payment-intent")
    suspend fun createPaymentIntent(@Body request: PaymentIntentCreateRequest): PaymentIntentResponse
}

