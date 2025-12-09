package com.example.flowershop.data.repository

import com.example.flowershop.data.api.ApiService
import com.example.flowershop.data.models.Order
import com.example.flowershop.data.models.OrderCreate
import com.example.flowershop.data.models.PaymentIntentCreateRequest
import com.example.flowershop.data.models.PaymentIntentResponse
import com.example.flowershop.util.Resource
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class OrderRepository @Inject constructor(
    private val apiService: ApiService
) {
    
    fun createOrder(orderCreate: OrderCreate): Flow<Resource<Order>> = flow {
        try {
            emit(Resource.Loading())
            val order = apiService.createOrder(orderCreate)
            emit(Resource.Success(order))
        } catch (e: HttpException) {
            emit(Resource.Error(e.localizedMessage ?: "An unexpected error occurred"))
        } catch (e: IOException) {
            emit(Resource.Error("Couldn't reach server. Check your internet connection."))
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "An unexpected error occurred"))
        }
    }
    
    fun getOrders(): Flow<Resource<List<Order>>> = flow {
        try {
            emit(Resource.Loading())
            val orders = apiService.getOrders()
            emit(Resource.Success(orders))
        } catch (e: HttpException) {
            emit(Resource.Error(e.localizedMessage ?: "An unexpected error occurred"))
        } catch (e: IOException) {
            emit(Resource.Error("Couldn't reach server. Check your internet connection."))
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "An unexpected error occurred"))
        }
    }
    
    fun cancelOrder(orderId: Int): Flow<Resource<Order>> = flow {
        try {
            emit(Resource.Loading())
            val order = apiService.cancelOrder(orderId)
            emit(Resource.Success(order))
        } catch (e: HttpException) {
            emit(Resource.Error(e.localizedMessage ?: "An unexpected error occurred"))
        } catch (e: IOException) {
            emit(Resource.Error("Couldn't reach server. Check your internet connection."))
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "An unexpected error occurred"))
        }
    }
    
    fun createPaymentIntent(orderId: Int): Flow<Resource<PaymentIntentResponse>> = flow {
        try {
            emit(Resource.Loading())
            val request = PaymentIntentCreateRequest(orderId)
            val response = apiService.createPaymentIntent(request)
            emit(Resource.Success(response))
        } catch (e: HttpException) {
            emit(Resource.Error(e.localizedMessage ?: "An unexpected error occurred"))
        } catch (e: IOException) {
            emit(Resource.Error("Couldn't reach server. Check your internet connection."))
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "An unexpected error occurred"))
        }
    }
    
    suspend fun processPayment(orderId: Int): Resource<Unit> {
        return try {
            apiService.processPayment(orderId)
            Resource.Success(Unit)
        } catch (e: HttpException) {
            Resource.Error(e.localizedMessage ?: "An unexpected error occurred")
        } catch (e: IOException) {
            Resource.Error("Couldn't reach server. Check your internet connection.")
        } catch (e: Exception) {
            Resource.Error(e.localizedMessage ?: "An unexpected error occurred")
        }
    }
}

