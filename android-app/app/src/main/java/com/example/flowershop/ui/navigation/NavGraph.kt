package com.example.flowershop.ui.navigation

import androidx.compose.runtime.Composable
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.example.flowershop.data.models.Order
import com.example.flowershop.ui.screens.*
import com.example.flowershop.ui.viewmodel.AuthViewModel
import com.example.flowershop.ui.viewmodel.OrderViewModel
import com.example.flowershop.ui.viewmodel.ProductViewModel
import com.google.gson.Gson

sealed class Screen(val route: String) {
    object Auth : Screen("auth")
    object Home : Screen("home")
    object Cart : Screen("cart")
    object Orders : Screen("orders")
    object Payment : Screen("payment/{order}") {
        fun createRoute(order: Order): String {
            val orderJson = Gson().toJson(order)
            return "payment/$orderJson"
        }
    }
}

@Composable
fun NavGraph(
    navController: NavHostController,
    startDestination: String,
    authViewModel: AuthViewModel,
    productViewModel: ProductViewModel,
    orderViewModel: OrderViewModel
) {
    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        composable(Screen.Auth.route) {
            AuthScreen(
                authViewModel = authViewModel,
                onAuthSuccess = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Auth.route) { inclusive = true }
                    }
                }
            )
        }
        
        composable(Screen.Home.route) {
            HomeScreen(
                authViewModel = authViewModel,
                productViewModel = productViewModel,
                orderViewModel = orderViewModel,
                onLogout = {
                    navController.navigate(Screen.Auth.route) {
                        popUpTo(0) { inclusive = true }
                    }
                },
                onNavigateToCart = {
                    navController.navigate(Screen.Cart.route)
                },
                onNavigateToOrders = {
                    navController.navigate(Screen.Orders.route)
                }
            )
        }
        
        composable(Screen.Cart.route) {
            CartScreen(
                productViewModel = productViewModel,
                orderViewModel = orderViewModel,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onOrderPlaced = {
                    navController.navigate(Screen.Orders.route) {
                        popUpTo(Screen.Home.route)
                    }
                }
            )
        }
        
        composable(Screen.Orders.route) {
            OrdersScreen(
                orderViewModel = orderViewModel,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onPaymentClick = { order ->
                    navController.navigate(Screen.Payment.createRoute(order))
                }
            )
        }
        
        composable(
            route = Screen.Payment.route,
            arguments = listOf(navArgument("order") { type = NavType.StringType })
        ) { backStackEntry ->
            val orderJson = backStackEntry.arguments?.getString("order")
            val order = Gson().fromJson(orderJson, Order::class.java)
            
            PaymentScreen(
                order = order,
                orderViewModel = orderViewModel,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onPaymentSuccess = {
                    navController.navigate(Screen.Orders.route) {
                        popUpTo(Screen.Orders.route) { inclusive = true }
                    }
                }
            )
        }
    }
}

