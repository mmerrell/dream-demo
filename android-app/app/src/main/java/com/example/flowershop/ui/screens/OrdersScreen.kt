package com.example.flowershop.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.flowershop.data.models.Order
import com.example.flowershop.ui.viewmodel.OrderViewModel
import java.math.BigDecimal

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OrdersScreen(
    orderViewModel: OrderViewModel,
    onNavigateBack: () -> Unit,
    onPaymentClick: (Order) -> Unit
) {
    val orderState by orderViewModel.orderState.collectAsState()
    val orderFilters by orderViewModel.orderFilters.collectAsState()
    val filteredOrders = orderViewModel.getFilteredOrders()
    
    LaunchedEffect(Unit) {
        orderViewModel.loadOrders()
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Your Orders") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Filter chips
            LazyRow(
                modifier = Modifier.fillMaxWidth(),
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                item {
                    FilterChip(
                        selected = orderFilters.pending,
                        onClick = { orderViewModel.toggleFilter("pending") },
                        label = { Text("⏳ Pending") }
                    )
                }
                item {
                    FilterChip(
                        selected = orderFilters.paid,
                        onClick = { orderViewModel.toggleFilter("paid") },
                        label = { Text("💳 Paid") }
                    )
                }
                item {
                    FilterChip(
                        selected = orderFilters.processing,
                        onClick = { orderViewModel.toggleFilter("processing") },
                        label = { Text("📦 Processing") }
                    )
                }
                item {
                    FilterChip(
                        selected = orderFilters.completed,
                        onClick = { orderViewModel.toggleFilter("completed") },
                        label = { Text("✓ Completed") }
                    )
                }
                item {
                    FilterChip(
                        selected = orderFilters.cancelled,
                        onClick = { orderViewModel.toggleFilter("cancelled") },
                        label = { Text("✗ Cancelled") }
                    )
                }
                item {
                    FilterChip(
                        selected = orderFilters.payment_failed,
                        onClick = { orderViewModel.toggleFilter("payment_failed") },
                        label = { Text("⚠ Payment Failed") }
                    )
                }
            }
            
            Divider()
            
            if (orderState.isLoading) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            } else if (orderState.error != null) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            text = orderState.error!!,
                            color = MaterialTheme.colorScheme.error
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(onClick = { orderViewModel.loadOrders() }) {
                            Text("Retry")
                        }
                    }
                }
            } else if (filteredOrders.isEmpty()) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "No orders to display",
                        style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(filteredOrders) { order ->
                        OrderCard(
                            order = order,
                            onPayClick = { onPaymentClick(order) },
                            onCancelClick = { orderViewModel.cancelOrder(order.id) }
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun OrderCard(
    order: Order,
    onPayClick: () -> Unit,
    onCancelClick: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Order #${order.id}",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                OrderStatusChip(status = order.status)
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Order items
            order.items.forEach { item ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "Product ID: ${item.product_id}",
                        style = MaterialTheme.typography.bodyMedium
                    )
                    Text(
                        text = "Qty: ${item.quantity}",
                        style = MaterialTheme.typography.bodyMedium
                    )
                    Text(
                        text = "$${BigDecimal(item.price_at_purchase).setScale(2)}",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
            
            Divider(modifier = Modifier.padding(vertical = 8.dp))
            
            Text(
                text = "Total: $${order.getTotalAmount()}",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
            
            // Action buttons for pending orders
            if (order.status == "pending") {
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Button(
                        onClick = onPayClick,
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Pay Now")
                    }
                    OutlinedButton(
                        onClick = onCancelClick,
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Cancel Order")
                    }
                }
            }
        }
    }
}

@Composable
fun OrderStatusChip(status: String) {
    val (color, emoji) = when (status) {
        "pending" -> Pair(MaterialTheme.colorScheme.tertiary, "⏳")
        "paid" -> Pair(MaterialTheme.colorScheme.primary, "✓")
        "processing" -> Pair(MaterialTheme.colorScheme.secondary, "📦")
        "completed" -> Pair(MaterialTheme.colorScheme.primaryContainer, "✓✓")
        "cancelled" -> Pair(MaterialTheme.colorScheme.error, "✗")
        "payment_failed" -> Pair(MaterialTheme.colorScheme.error, "⚠")
        else -> Pair(MaterialTheme.colorScheme.surface, "?")
    }
    
    Surface(
        color = color,
        shape = MaterialTheme.shapes.small
    ) {
        Text(
            text = "$emoji ${status.uppercase()}",
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            style = MaterialTheme.typography.labelMedium,
            fontWeight = FontWeight.Bold
        )
    }
}

