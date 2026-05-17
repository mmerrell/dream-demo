// Test-only helper to pre-seed auth token into DataStore via adb for tests
// Usage: adb shell am broadcast -a com.example.flowershop.SET_TEST_TOKEN --es token "<TOKEN>"

package com.example.flowershop.testutils

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.runBlocking

private val Context.dataStore by preferencesDataStore("user_prefs")

class TestTokenReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val token = intent.getStringExtra("token") ?: return
        val AUTH_TOKEN_KEY = stringPreferencesKey("auth_token")
        runBlocking {
            context.dataStore.edit { prefs ->
                prefs[AUTH_TOKEN_KEY] = token
            }
        }
    }
}
