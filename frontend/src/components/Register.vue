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

    <div class="flex-1 flex items-center justify-center px-4 py-12">
      <div class="w-full max-w-md bg-white rounded-2xl shadow-lg overflow-hidden">

        <!-- Card header -->
        <div class="px-8 pt-8 pb-6 text-center" style="background: linear-gradient(135deg, #7c3aed, #db2777);">
          <img src="../assets/huskyvoice-logo.jpg" alt="HuskyVoice.AI" class="w-16 h-16 rounded-full mx-auto mb-3 border-4 border-white shadow" />
          <h1 class="text-white text-xl font-bold">HuskyVoice.AI</h1>
          <p class="text-purple-100 text-sm mt-1">Leave Management Portal</p>
        </div>

        <div class="px-8 py-7">
          <h2 class="text-gray-800 text-lg font-semibold mb-5">Create your account</h2>

          <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm whitespace-pre-line">{{ error }}</div>
          <div v-if="success" class="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm">{{ success }}</div>

          <!-- Role toggle -->
          <div class="flex rounded-lg overflow-hidden border border-gray-200 mb-5">
            <button type="button" @click="form.role = 'employee'"
              :class="['flex-1 py-2 text-sm font-semibold transition-all',
                form.role === 'employee' ? 'text-white' : 'bg-white text-gray-500 hover:bg-gray-50']"
              :style="form.role === 'employee' ? 'background: linear-gradient(90deg, #7c3aed, #db2777)' : ''">
              👤 Employee
            </button>
            <button type="button" @click="form.role = 'employer'"
              :class="['flex-1 py-2 text-sm font-semibold transition-all',
                form.role === 'employer' ? 'text-white' : 'bg-white text-gray-500 hover:bg-gray-50']"
              :style="form.role === 'employer' ? 'background: linear-gradient(90deg, #7c3aed, #db2777)' : ''">
              🏢 Employer
            </button>
          </div>

          <div class="grid grid-cols-2 gap-3 mb-4">
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">First Name</label>
              <input v-model="form.first_name" type="text" placeholder="John"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Last Name</label>
              <input v-model="form.last_name" type="text" placeholder="Doe"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400" />
            </div>
          </div>

          <div class="mb-4">
            <label class="block text-xs font-medium text-gray-700 mb-1">Username</label>
            <input v-model="form.username" type="text" placeholder="johndoe"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400" />
          </div>

          <div class="mb-4">
            <label class="block text-xs font-medium text-gray-700 mb-1">Email</label>
            <input v-model="form.email" type="email" placeholder="john@example.com"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400" />
          </div>

          <div class="grid grid-cols-2 gap-3 mb-6">
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Password</label>
              <input v-model="form.password" type="password" placeholder="Min. 6 chars"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Confirm Password</label>
              <input v-model="form.password2" type="password" placeholder="Repeat"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400" />
            </div>
          </div>

          <button @click="handleRegister" :disabled="loading"
            class="w-full py-2.5 text-white font-semibold rounded-lg transition-opacity disabled:opacity-50"
            style="background: linear-gradient(90deg, #7c3aed, #db2777);">
            {{ loading ? 'Creating account...' : 'Create Account' }}
          </button>

          <p class="text-center text-sm text-gray-500 mt-5">
            Already have an account?
            <router-link to="/login" class="font-semibold" style="color: #7c3aed;">Sign in</router-link>
          </p>
        </div>
      </div>
    </div>

    <footer class="text-center py-4 text-xs text-gray-400">
      © 2025 HuskyVoice.AI · All rights reserved
    </footer>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'Register',
  data() {
    return {
      form: { username: '', email: '', first_name: '', last_name: '', password: '', password2: '', role: 'employee' },
      loading: false, error: '', success: ''
    }
  },
  methods: {
    async handleRegister() {
      this.error = ''; this.success = ''
      if (!this.form.username || !this.form.email || !this.form.password) { this.error = 'Please fill in all required fields.'; return }
      if (this.form.password !== this.form.password2) { this.error = 'Passwords do not match.'; return }
      if (this.form.password.length < 6) { this.error = 'Password must be at least 6 characters.'; return }
      this.loading = true
      try {
        const { password2, ...dataToSend } = this.form
        const response = await api.post('/auth/register/', dataToSend)
        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        this.success = 'Account created! Redirecting...'
        setTimeout(() => {
          const role = response.data.user?.role || 'employee'
          this.$router.push(role === 'employer' ? '/employer/dashboard' : '/employee/dashboard')
        }, 1000)
      } catch (err) {
        const data = err.response?.data
        if (data && typeof data === 'object') {
          this.error = Object.entries(data).map(([f, m]) => `${f}: ${Array.isArray(m) ? m.join(', ') : m}`).join('\n')
        } else { this.error = 'Registration failed. Please try again.' }
      } finally { this.loading = false }
    }
  }
}
</script>
