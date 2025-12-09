package com.example.flowershop.data.models

data class User(
    val id: Int,
    val email: String,
    val is_active: Boolean
)

data class UserCreate(
    val email: String,
    val password: String
)

data class Token(
    val access_token: String,
    val token_type: String
)

