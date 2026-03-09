<template>
  <div class="min-h-screen bg-gray-50">

    <!-- Navbar -->
    <nav class="bg-white shadow-sm sticky top-0 z-10">
      <div class="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <img src="../assets/huskyvoice-logo.jpg" alt="HuskyVoice.AI" class="w-9 h-9 rounded-full" />
          <div>
            <span class="font-bold text-base" style="background: linear-gradient(90deg, #7c3aed, #db2777); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">HuskyVoice.AI</span>
            <p class="text-xs text-gray-400 leading-none">Leave Management</p>
          </div>
        </div>
        <div class="flex items-center gap-4">
          <div class="text-right">
            <p class="text-sm font-medium text-gray-700">{{ user?.first_name || user?.username }}</p>
            <p class="text-xs text-purple-500 font-medium">Employee</p>
          </div>
          <button @click="logout"
            class="text-sm px-4 py-2 rounded-lg text-white font-medium"
            style="background: linear-gradient(90deg, #7c3aed, #db2777);">
            Logout
          </button>
        </div>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto px-4 py-8">

      <!-- Header row -->
      <div class="flex justify-between items-center mb-6">
        <div>
          <h2 class="text-xl font-bold text-gray-800">My Leave Requests</h2>
          <p class="text-sm text-gray-500">Manage your leave applications</p>
        </div>
        <button @click="showForm = !showForm"
          class="text-sm px-5 py-2.5 rounded-lg text-white font-semibold shadow"
          style="background: linear-gradient(90deg, #7c3aed, #db2777);">
          {{ showForm ? '✕ Cancel' : '+ Apply for Leave' }}
        </button>
      </div>

      <!-- Apply Form -->
      <div v-if="showForm" class="bg-white rounded-2xl shadow-sm border border-purple-100 p-6 mb-6">
        <h3 class="font-semibold text-gray-700 mb-4 flex items-center gap-2">
          <span class="w-1 h-5 rounded-full inline-block" style="background: linear-gradient(#7c3aed, #db2777);"></span>
          New Leave Application
        </h3>

        <div v-if="formError" class="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">{{ formError }}</div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Leave Type <span class="text-red-400">*</span></label>
            <select v-model="leaveForm.leave_type" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400">
              <option value="sick">🤒 Sick Leave</option>
              <option value="casual">🌴 Casual Leave</option>
              <option value="annual">📅 Annual Leave</option>
              <option value="other">📋 Other</option>
            </select>
          </div>
          <div></div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Start Date <span class="text-red-400">*</span></label>
            <input v-model="leaveForm.start_date" type="date" :min="today"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">End Date <span class="text-red-400">*</span></label>
            <input v-model="leaveForm.end_date" type="date" :min="leaveForm.start_date || today"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400" />
          </div>
          <div class="sm:col-span-2">
            <label class="block text-xs font-medium text-gray-600 mb-1">Reason <span class="text-red-400">*</span></label>
            <textarea v-model="leaveForm.reason" rows="3" placeholder="Briefly explain your reason..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400"></textarea>
          </div>
        </div>

        <div class="mt-4 flex gap-3">
          <button @click="submitLeave" :disabled="submitting"
            class="px-6 py-2 text-white text-sm font-semibold rounded-lg disabled:opacity-50"
            style="background: linear-gradient(90deg, #7c3aed, #db2777);">
            {{ submitting ? 'Submitting...' : 'Submit Application' }}
          </button>
          <button @click="showForm = false; formError = ''"
            class="px-6 py-2 bg-gray-100 hover:bg-gray-200 text-gray-600 text-sm font-medium rounded-lg">
            Cancel
          </button>
        </div>
      </div>

      <!-- Stats row -->
      <div class="grid grid-cols-3 gap-4 mb-6">
        <div class="bg-white rounded-xl p-4 shadow-sm text-center border-t-4 border-yellow-400">
          <p class="text-2xl font-bold text-yellow-600">{{ leaves.filter(l => l.status === 'pending').length }}</p>
          <p class="text-xs text-gray-500 mt-1">Pending</p>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-sm text-center border-t-4 border-green-400">
          <p class="text-2xl font-bold text-green-600">{{ leaves.filter(l => l.status === 'approved').length }}</p>
          <p class="text-xs text-gray-500 mt-1">Approved</p>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-sm text-center border-t-4 border-red-400">
          <p class="text-2xl font-bold text-red-600">{{ leaves.filter(l => l.status === 'rejected').length }}</p>
          <p class="text-xs text-gray-500 mt-1">Rejected</p>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-10 text-gray-400">Loading your leaves...</div>

      <!-- Empty -->
      <div v-else-if="leaves.length === 0" class="bg-white rounded-2xl shadow-sm p-12 text-center">
        <p class="text-4xl mb-3">📋</p>
        <p class="text-gray-600 font-medium">No leave applications yet</p>
        <p class="text-sm text-gray-400 mt-1">Click "Apply for Leave" to get started</p>
      </div>

      <!-- Leave cards -->
      <div v-else class="space-y-4">
        <div v-for="leave in leaves" :key="leave.id"
          class="bg-white rounded-2xl shadow-sm p-5 border-l-4"
          :class="{
            'border-yellow-400': leave.status === 'pending',
            'border-green-500': leave.status === 'approved',
            'border-red-500': leave.status === 'rejected'
          }">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1">
                <span class="font-semibold text-gray-800 capitalize">{{ leaveTypeLabel(leave.leave_type) }}</span>
              </div>
              <p class="text-sm text-gray-500">📅 {{ formatDate(leave.start_date) }} → {{ formatDate(leave.end_date) }}</p>
              <p class="text-sm text-gray-600 mt-2">{{ leave.reason }}</p>
              <p v-if="leave.comments" class="text-sm text-gray-400 mt-1 italic">💬 "{{ leave.comments }}"</p>
            </div>
            <span class="text-xs font-bold px-3 py-1 rounded-full capitalize ml-4"
              :class="{
                'bg-yellow-100 text-yellow-700': leave.status === 'pending',
                'bg-green-100 text-green-700': leave.status === 'approved',
                'bg-red-100 text-red-700': leave.status === 'rejected'
              }">
              {{ leave.status }}
            </span>
          </div>
          <p class="text-xs text-gray-400 mt-3 pt-3 border-t border-gray-100">Applied: {{ formatDateTime(leave.applied_on) }}</p>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="text-center py-6 text-xs text-gray-400 mt-8">
      © 2025 HuskyVoice.AI · Leave Management System
    </footer>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'EmployeeDashboard',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user') || '{}'),
      leaves: [], loading: true, showForm: false, submitting: false, formError: '',
      leaveForm: { leave_type: 'sick', start_date: '', end_date: '', reason: '' }
    }
  },
  computed: {
    today() { return new Date().toISOString().split('T')[0] }
  },
  mounted() { this.fetchLeaves() },
  methods: {
    leaveTypeLabel(t) {
      return { sick: '🤒 Sick Leave', casual: '🌴 Casual Leave', annual: '📅 Annual Leave', other: '📋 Other' }[t] || t
    },
    formatDate(d) {
      if (!d) return '-'
      return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    },
    formatDateTime(d) {
      if (!d) return '-'
      return new Date(d).toLocaleString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
    },
    async fetchLeaves() {
      this.loading = true
      try {
        const r = await api.get('/leaves/')
        this.leaves = r.data
      } catch (err) {
        if (err.response?.status === 401) this.$router.push('/login')
      } finally { this.loading = false }
    },
    async submitLeave() {
      this.formError = ''
      if (!this.leaveForm.start_date || !this.leaveForm.end_date || !this.leaveForm.reason.trim()) {
        this.formError = 'Please fill in all required fields.'; return
      }
      if (this.leaveForm.end_date < this.leaveForm.start_date) {
        this.formError = 'End date cannot be before start date.'; return
      }
      this.submitting = true
      try {
        await api.post('/leaves/', this.leaveForm)
        this.showForm = false
        this.leaveForm = { leave_type: 'sick', start_date: '', end_date: '', reason: '' }
        await this.fetchLeaves()
      } catch (err) {
        const data = err.response?.data
        this.formError = data ? Object.values(data).flat().join(' ') : 'Failed to submit.'
      } finally { this.submitting = false }
    },
    logout() { localStorage.clear(); this.$router.push('/login') }
  }
}
</script>
