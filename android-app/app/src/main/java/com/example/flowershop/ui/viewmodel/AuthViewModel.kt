package com.example.flowershop.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.flowershop.data.models.User
import com.example.flowershop.data.repository.AuthRepository
import com.example.flowershop.util.Resource
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class AuthState(
    val isLoading: Boolean = false,
    val user: User? = null,
    val error: String? = null,
    val isAuthenticated: Boolean = false
)

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    private val _authState = MutableStateFlow(AuthState())
    val authState: StateFlow<AuthState> = _authState.asStateFlow()
    
    init {
        checkAuthStatus()
    }
    
    private fun checkAuthStatus() {
        viewModelScope.launch {
            authRepository.getAuthToken().collect { token ->
                if (token != null) {
                    getCurrentUser()
                }
            }
        }
    }
    
    fun login(email: String, password: String) {
        viewModelScope.launch {
            authRepository.login(email, password).collect { result ->
                when (result) {
                    is Resource.Loading -> {
                        _authState.value = _authState.value.copy(isLoading = true, error = null)
                    }
                    is Resource.Success -> {
                        _authState.value = AuthState(
                            isLoading = false,
                            user = result.data,
                            isAuthenticated = true,
                            error = null
                        )
                    }
                    is Resource.Error -> {
                        _authState.value = _authState.value.copy(
                            isLoading = false,
                            error = result.message,
                            isAuthenticated = false
                        )
                    }
                }
            }
        }
    }
    
    fun register(email: String, password: String) {
        viewModelScope.launch {
            authRepository.register(email, password).collect { result ->
                when (result) {
                    is Resource.Loading -> {
                        _authState.value = _authState.value.copy(isLoading = true, error = null)
                    }
                    is Resource.Success -> {
                        _authState.value = _authState.value.copy(
                            isLoading = false,
                            error = null
                        )
                    }
                    is Resource.Error -> {
                        _authState.value = _authState.value.copy(
                            isLoading = false,
                            error = result.message
                        )
                    }
                }
            }
        }
    }
    
    private fun getCurrentUser() {
        viewModelScope.launch {
            authRepository.getCurrentUser().collect { result ->
                when (result) {
                    is Resource.Success -> {
                        _authState.value = AuthState(
                            isLoading = false,
                            user = result.data,
                            isAuthenticated = true,
                            error = null
                        )
                    }
                    is Resource.Error -> {
                        _authState.value = AuthState(
                            isLoading = false,
                            user = null,
                            isAuthenticated = false,
                            error = null
                        )
                    }
                    is Resource.Loading -> {
                        // Do nothing
                    }
                }
            }
        }
    }
    
    fun logout() {
        viewModelScope.launch {
            authRepository.logout()
            _authState.value = AuthState()
        }
    }
    
    fun clearError() {
        _authState.value = _authState.value.copy(error = null)
    }
}

