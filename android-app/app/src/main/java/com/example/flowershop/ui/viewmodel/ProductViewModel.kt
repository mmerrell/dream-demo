package com.example.flowershop.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.flowershop.data.models.CartItem
import com.example.flowershop.data.models.Product
import com.example.flowershop.data.repository.ProductRepository
import com.example.flowershop.util.Resource
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.math.BigDecimal
import javax.inject.Inject

data class ProductState(
    val isLoading: Boolean = false,
    val products: List<Product> = emptyList(),
    val error: String? = null
)

@HiltViewModel
class ProductViewModel @Inject constructor(
    private val productRepository: ProductRepository
) : ViewModel() {
    
    private val _productState = MutableStateFlow(ProductState())
    val productState: StateFlow<ProductState> = _productState.asStateFlow()
    
    private val _cart = MutableStateFlow<Map<Int, Int>>(emptyMap())
    val cart: StateFlow<Map<Int, Int>> = _cart.asStateFlow()
    
    init {
        loadProducts()
    }
    
    fun loadProducts() {
        viewModelScope.launch {
            productRepository.getProducts().collect { result ->
                when (result) {
                    is Resource.Loading -> {
                        _productState.value = _productState.value.copy(isLoading = true, error = null)
                    }
                    is Resource.Success -> {
                        _productState.value = ProductState(
                            isLoading = false,
                            products = result.data ?: emptyList(),
                            error = null
                        )
                    }
                    is Resource.Error -> {
                        _productState.value = _productState.value.copy(
                            isLoading = false,
                            error = result.message
                        )
                    }
                }
            }
        }
    }
    
    fun addToCart(productId: Int) {
        val currentCart = _cart.value.toMutableMap()
        currentCart[productId] = (currentCart[productId] ?: 0) + 1
        _cart.value = currentCart
    }
    
    fun removeFromCart(productId: Int) {
        val currentCart = _cart.value.toMutableMap()
        val currentQty = currentCart[productId] ?: 0
        
        if (currentQty > 1) {
            currentCart[productId] = currentQty - 1
        } else {
            currentCart.remove(productId)
        }
        
        _cart.value = currentCart
    }
    
    fun clearCart() {
        _cart.value = emptyMap()
    }
    
    fun getCartItems(): List<CartItem> {
        return _cart.value.mapNotNull { (productId, quantity) ->
            val product = _productState.value.products.find { it.id == productId }
            product?.let { CartItem(it, quantity) }
        }
    }
    
    fun getCartTotal(): BigDecimal {
        return getCartItems().fold(BigDecimal.ZERO) { acc, item ->
            acc + (item.product.getPriceDecimal() * item.quantity.toBigDecimal())
        }
    }
}

