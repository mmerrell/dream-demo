package com.example.flowershop.ui.screens

import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import com.example.flowershop.BuildConfig
import com.example.flowershop.data.models.Order
import com.example.flowershop.ui.viewmodel.OrderViewModel
import com.stripe.android.PaymentConfiguration
import com.stripe.android.paymentsheet.PaymentSheet
import com.stripe.android.paymentsheet.PaymentSheetResult
import com.stripe.android.paymentsheet.rememberPaymentSheet
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PaymentScreen(
    order: Order,
    orderViewModel: OrderViewModel,
    onNavigateBack: () -> Unit,
    onPaymentSuccess: () -> Unit
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val orderState by orderViewModel.orderState.collectAsState()
    
    val paymentSheet = rememberPaymentSheet { result ->
        when (result) {
            is PaymentSheetResult.Completed -> {
                scope.launch {
                    // Process payment on backend
                    val processResult = orderViewModel.processPayment(order.id)
                    if (processResult is com.example.flowershop.util.Resource.Success) {
                        Toast.makeText(context, "Payment successful!", Toast.LENGTH_SHORT).show()
                        orderViewModel.loadOrders()
                        onPaymentSuccess()
                    } else {
                        Toast.makeText(
                            context,
                            "Payment succeeded but order processing failed",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                }
            }
            is PaymentSheetResult.Canceled -> {
                Toast.makeText(context, "Payment canceled", Toast.LENGTH_SHORT).show()
            }
            is PaymentSheetResult.Failed -> {
                Toast.makeText(
                    context,
                    "Payment failed: ${result.error.message}",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }
    
    // Initialize Stripe
    LaunchedEffect(Unit) {
        PaymentConfiguration.init(context, BuildConfig.STRIPE_PUBLISHABLE_KEY)
        orderViewModel.createPaymentIntent(order.id)
    }
    
    // Launch payment sheet when client secret is ready
    LaunchedEffect(orderState.paymentIntent) {
        orderState.paymentIntent?.let { paymentIntent ->
            paymentSheet.presentWithPaymentIntent(
                paymentIntent.client_secret,
                PaymentSheet.Configuration(
                    merchantDisplayName = "Flower Shop"
                )
            )
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Payment") },
                navigationIcon = {
                    IconButton(onClick = {
                        orderViewModel.clearPaymentIntent()
                        onNavigateBack()
                    }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentAlignment = Alignment.Center
        ) {
            if (orderState.isLoading) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    CircularProgressIndicator()
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("Preparing payment...")
                }
            } else if (orderState.error != null) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    modifier = Modifier.padding(32.dp)
                ) {
                    Text(
                        text = "Error: ${orderState.error}",
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodyLarge
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(onClick = {
                        orderViewModel.clearError()
                        onNavigateBack()
                    }) {
                        Text("Go Back")
                    }
                }
            } else {
                // Payment info
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Order #${order.id}",
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "Total: $${order.getTotalAmount()}",
                        style = MaterialTheme.typography.displaySmall,
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(24.dp))
                    Text(
                        text = "Payment sheet will open automatically...",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}

