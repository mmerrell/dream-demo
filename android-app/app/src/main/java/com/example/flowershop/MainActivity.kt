package com.example.flowershop

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.compose.rememberNavController
import com.example.flowershop.ui.navigation.NavGraph
import com.example.flowershop.ui.navigation.Screen
import com.example.flowershop.ui.theme.FlowerShopTheme
import com.example.flowershop.ui.viewmodel.AuthViewModel
import com.example.flowershop.ui.viewmodel.OrderViewModel
import com.example.flowershop.ui.viewmodel.ProductViewModel
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            FlowerShopTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val navController = rememberNavController()
                    val authViewModel: AuthViewModel = hiltViewModel()
                    val productViewModel: ProductViewModel = hiltViewModel()
                    val orderViewModel: OrderViewModel = hiltViewModel()
                    
                    val authState by authViewModel.authState.collectAsState()
                    val startDestination = if (authState.isAuthenticated) {
                        Screen.Home.route
                    } else {
                        Screen.Auth.route
                    }
                    
                    NavGraph(
                        navController = navController,
                        startDestination = startDestination,
                        authViewModel = authViewModel,
                        productViewModel = productViewModel,
                        orderViewModel = orderViewModel
                    )
                }
            }
        }
    }
}

