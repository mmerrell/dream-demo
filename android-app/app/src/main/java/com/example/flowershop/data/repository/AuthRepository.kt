package com.example.flowershop.data.repository

import com.example.flowershop.data.api.ApiService
import com.example.flowershop.data.local.PreferencesManager
import com.example.flowershop.data.models.User
import com.example.flowershop.data.models.UserCreate
import com.example.flowershop.util.Resource
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val apiService: ApiService,
    private val preferencesManager: PreferencesManager
) {
    
    fun login(email: String, password: String): Flow<Resource<User>> = flow {
        try {
            emit(Resource.Loading())
            
            // Login and get token
            val tokenResponse = apiService.login(email, password)
            
            // Save token
            preferencesManager.saveAuthToken(tokenResponse.access_token)
            preferencesManager.saveUserEmail(email)
            
            // Get user info
            val user = apiService.getCurrentUser()
            emit(Resource.Success(user))
        } catch (e: HttpException) {
            emit(Resource.Error(e.localizedMessage ?: "An unexpected error occurred"))
        } catch (e: IOException) {
            emit(Resource.Error("Couldn't reach server. Check your internet connection."))
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "An unexpected error occurred"))
        }
    }
    
    fun register(email: String, password: String): Flow<Resource<User>> = flow {
        try {
            emit(Resource.Loading())
            
            val userCreate = UserCreate(email, password)
            val user = apiService.register(userCreate)
            
            emit(Resource.Success(user))
        } catch (e: HttpException) {
            emit(Resource.Error(e.localizedMessage ?: "An unexpected error occurred"))
        } catch (e: IOException) {
            emit(Resource.Error("Couldn't reach server. Check your internet connection."))
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "An unexpected error occurred"))
        }
    }
    
    fun getCurrentUser(): Flow<Resource<User>> = flow {
        try {
            emit(Resource.Loading())
            val user = apiService.getCurrentUser()
            emit(Resource.Success(user))
        } catch (e: HttpException) {
            emit(Resource.Error(e.localizedMessage ?: "An unexpected error occurred"))
        } catch (e: IOException) {
            emit(Resource.Error("Couldn't reach server. Check your internet connection."))
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "An unexpected error occurred"))
        }
    }
    
    suspend fun logout() {
        preferencesManager.clearAuthData()
    }
    
    fun getAuthToken(): Flow<String?> = preferencesManager.authToken
}

