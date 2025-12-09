package com.example.flowershop.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.flowershop.data.models.Order
import com.example.flowershop.data.models.OrderCreate
import com.example.flowershop.data.models.OrderItemCreate
import com.example.flowershop.data.models.PaymentIntentResponse
import com.example.flowershop.data.repository.OrderRepository
import com.example.flowershop.util.Resource
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class OrderState(
    val isLoading: Boolean = false,
    val orders: List<Order> = emptyList(),
    val error: String? = null,
    val orderCreated: Boolean = false,
    val paymentIntent: PaymentIntentResponse? = null
)

data class OrderFilters(
    val pending: Boolean = true,
    val paid: Boolean = true,
    val processing: Boolean = true,
    val completed: Boolean = false,
    val cancelled: Boolean = false,
    val payment_failed: Boolean = false
)

@HiltViewModel
class OrderViewModel @Inject constructor(
    private val orderRepository: OrderRepository
) : ViewModel() {
    
    private val _orderState = MutableStateFlow(OrderState())
    val orderState: StateFlow<OrderState> = _orderState.asStateFlow()
    
    private val _orderFilters = MutableStateFlow(OrderFilters())
    val orderFilters: StateFlow<OrderFilters> = _orderFilters.asStateFlow()
    
    fun loadOrders() {
        viewModelScope.launch {
            orderRepository.getOrders().collect { result ->
                when (result) {
                    is Resource.Loading -> {
                        _orderState.value = _orderState.value.copy(isLoading = true, error = null)
                    }
                    is Resource.Success -> {
                        _orderState.value = _orderState.value.copy(
                            isLoading = false,
                            orders = result.data ?: emptyList(),
                            error = null
                        )
                    }
                    is Resource.Error -> {
                        _orderState.value = _orderState.value.copy(
                            isLoading = false,
                            error = result.message
                        )
                    }
                }
            }
        }
    }
    
    fun createOrder(cart: Map<Int, Int>) {
        viewModelScope.launch {
            val items = cart.map { (productId, quantity) ->
                OrderItemCreate(productId, quantity)
            }
            val orderCreate = OrderCreate(items)
            
            orderRepository.createOrder(orderCreate).collect { result ->
                when (result) {
                    is Resource.Loading -> {
                        _orderState.value = _orderState.value.copy(isLoading = true, error = null, orderCreated = false)
                    }
                    is Resource.Success -> {
                        _orderState.value = _orderState.value.copy(
                            isLoading = false,
                            error = null,
                            orderCreated = true
                        )
                        loadOrders() // Reload orders to show the new one
                    }
                    is Resource.Error -> {
                        _orderState.value = _orderState.value.copy(
                            isLoading = false,
                            error = result.message,
                            orderCreated = false
                        )
                    }
                }
            }
        }
    }
    
    fun cancelOrder(orderId: Int) {
        viewModelScope.launch {
            orderRepository.cancelOrder(orderId).collect { result ->
                when (result) {
                    is Resource.Loading -> {
                        _orderState.value = _orderState.value.copy(isLoading = true, error = null)
                    }
                    is Resource.Success -> {
                        _orderState.value = _orderState.value.copy(isLoading = false, error = null)
                        loadOrders() // Reload to show updated status
                    }
                    is Resource.Error -> {
                        _orderState.value = _orderState.value.copy(
                            isLoading = false,
                            error = result.message
                        )
                    }
                }
            }
        }
    }
    
    fun createPaymentIntent(orderId: Int) {
        viewModelScope.launch {
            orderRepository.createPaymentIntent(orderId).collect { result ->
                when (result) {
                    is Resource.Loading -> {
                        _orderState.value = _orderState.value.copy(isLoading = true, error = null)
                    }
                    is Resource.Success -> {
                        _orderState.value = _orderState.value.copy(
                            isLoading = false,
                            paymentIntent = result.data,
                            error = null
                        )
                    }
                    is Resource.Error -> {
                        _orderState.value = _orderState.value.copy(
                            isLoading = false,
                            error = result.message
                        )
                    }
                }
            }
        }
    }
    
    suspend fun processPayment(orderId: Int): Resource<Unit> {
        return orderRepository.processPayment(orderId)
    }
    
    fun toggleFilter(status: String) {
        val currentFilters = _orderFilters.value
        _orderFilters.value = when (status) {
            "pending" -> currentFilters.copy(pending = !currentFilters.pending)
            "paid" -> currentFilters.copy(paid = !currentFilters.paid)
            "processing" -> currentFilters.copy(processing = !currentFilters.processing)
            "completed" -> currentFilters.copy(completed = !currentFilters.completed)
            "cancelled" -> currentFilters.copy(cancelled = !currentFilters.cancelled)
            "payment_failed" -> currentFilters.copy(payment_failed = !currentFilters.payment_failed)
            else -> currentFilters
        }
    }
    
    fun getFilteredOrders(): List<Order> {
        val filters = _orderFilters.value
        return _orderState.value.orders.filter { order ->
            when (order.status) {
                "pending" -> filters.pending
                "paid" -> filters.paid
                "processing" -> filters.processing
                "completed" -> filters.completed
                "cancelled" -> filters.cancelled
                "payment_failed" -> filters.payment_failed
                else -> true
            }
        }
    }
    
    fun clearPaymentIntent() {
        _orderState.value = _orderState.value.copy(paymentIntent = null)
    }
    
    fun clearOrderCreated() {
        _orderState.value = _orderState.value.copy(orderCreated = false)
    }
    
    fun clearError() {
        _orderState.value = _orderState.value.copy(error = null)
    }
}

