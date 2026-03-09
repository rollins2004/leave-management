<template>
  <div class="min-h-screen flex flex-col" style="background: linear-gradient(135deg, #f5f3ff 0%, #fdf2f8 100%);">

    <!-- Top navbar -->
    <nav class="bg-white shadow-sm px-6 py-3 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <img src="../assets/huskyvoice-logo.jpg" alt="HuskyVoice.AI" class="w-9 h-9 rounded-full" />
        <span class="font-bold text-lg" style="background: linear-gradient(90deg, #7c3aed, #db2777); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">HuskyVoice.AI</span>
      </div>
      <span class="text-sm text-gray-500">Leave Management System</span>
    </nav>

    <!-- Login card -->
    <div class="flex-1 flex items-center justify-center px-4 py-12">
      <div class="w-full max-w-md bg-white rounded-2xl shadow-lg overflow-hidden">

        <!-- Card header -->
        <div class="px-8 pt-8 pb-6 text-center" style="background: linear-gradient(135deg, #7c3aed, #db2777);">
          <img src="../assets/huskyvoice-logo.jpg" alt="HuskyVoice.AI" class="w-16 h-16 rounded-full mx-auto mb-3 border-4 border-white shadow" />
          <h1 class="text-white text-xl font-bold">HuskyVoice.AI</h1>
          <p class="text-purple-100 text-sm mt-1">Leave Management Portal</p>
        </div>

        <!-- Form -->
        <div class="px-8 py-7">
          <h2 class="text-gray-800 text-lg font-semibold mb-5">Sign in to your account</h2>

          <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {{ error }}
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input v-model="username" type="text" placeholder="Enter your username"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400" />
          </div>

          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input v-model="password" type="password" placeholder="Enter your password"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400" />
          </div>

          <button @click="handleLogin" :disabled="loading || !username || !password"
            class="w-full py-2.5 text-white font-semibold rounded-lg transition-opacity disabled:opacity-50"
            style="background: linear-gradient(90deg, #7c3aed, #db2777);">
            {{ loading ? 'Signing in...' : 'Sign In' }}
          </button>

          <p class="text-center text-sm text-gray-500 mt-5">
            Don't have an account?
            <router-link to="/register" class="font-semibold" style="color: #7c3aed;">Register here</router-link>
          </p>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="text-center py-4 text-xs text-gray-400">
      © 2025 HuskyVoice.AI · All rights reserved
    </footer>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'Login',
  data() {
    return { username: '', password: '', loading: false, error: '' }
  },
  methods: {
    async handleLogin() {
      if (!this.username || !this.password) { this.error = 'Please enter username and password.'; return }
      this.loading = true; this.error = ''
      try {
        const response = await api.post('/auth/login/', { username: this.username, password: this.password })
        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        const role = response.data.user?.role || 'employee'
        this.$router.push(role === 'employer' ? '/employer/dashboard' : '/employee/dashboard')
      } catch (err) {
        const data = err.response?.data
        this.error = data?.non_field_errors?.[0] || data?.detail || 'Login failed. Please check your credentials.'
      } finally { this.loading = false }
    }
  }
}
</script>
