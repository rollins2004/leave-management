<template>
  <div class="min-h-screen bg-gray-50">

    <!-- Navbar -->
    <nav class="bg-white shadow-sm sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
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
            <p class="text-xs text-pink-500 font-medium">Employer</p>
          </div>
          <button @click="logout"
            class="text-sm px-4 py-2 rounded-lg text-white font-medium"
            style="background: linear-gradient(90deg, #7c3aed, #db2777);">
            Logout
          </button>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 py-8">

      <!-- Flash -->
      <div v-if="flashMessage" class="mb-4 p-3 rounded-lg text-sm font-medium"
        :class="flashType === 'success' ? 'bg-green-50 border border-green-200 text-green-700' : 'bg-red-50 border border-red-200 text-red-700'">
        {{ flashMessage }}
      </div>

      <!-- Page title -->
      <div class="mb-6">
        <h2 class="text-xl font-bold text-gray-800">Leave Requests</h2>
        <p class="text-sm text-gray-500">Review and manage employee leave applications</p>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-xl p-4 shadow-sm text-center border-t-4" style="border-color: #7c3aed;">
          <p class="text-2xl font-bold" style="color: #7c3aed;">{{ stats.total }}</p>
          <p class="text-xs text-gray-500 mt-1">Total</p>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-sm text-center border-t-4 border-yellow-400">
          <p class="text-2xl font-bold text-yellow-600">{{ stats.pending }}</p>
          <p class="text-xs text-gray-500 mt-1">Pending</p>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-sm text-center border-t-4 border-green-400">
          <p class="text-2xl font-bold text-green-600">{{ stats.approved }}</p>
          <p class="text-xs text-gray-500 mt-1">Approved</p>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-sm text-center border-t-4 border-red-400">
          <p class="text-2xl font-bold text-red-600">{{ stats.rejected }}</p>
          <p class="text-xs text-gray-500 mt-1">Rejected</p>
        </div>
      </div>

      <!-- Filter tabs -->
      <div class="flex gap-2 mb-4">
        <button v-for="f in filters" :key="f.value" @click="activeFilter = f.value"
          :class="['text-sm px-4 py-1.5 rounded-full border font-medium transition-all',
            activeFilter === f.value ? 'text-white border-transparent' : 'bg-white text-gray-500 border-gray-200 hover:border-purple-300']"
          :style="activeFilter === f.value ? 'background: linear-gradient(90deg, #7c3aed, #db2777)' : ''">
          {{ f.label }}
        </button>
      </div>

      <!-- Table -->
      <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div v-if="loading" class="py-12 text-center text-gray-400">Loading leave requests...</div>

        <table v-else class="min-w-full divide-y divide-gray-100">
          <thead>
            <tr style="background: linear-gradient(90deg, #f5f3ff, #fdf2f8);">
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Employee</th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Type</th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Duration</th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Reason</th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Status</th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="leave in filteredLeaves" :key="leave.id" class="hover:bg-purple-50 transition-colors">
              <td class="px-5 py-4">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold"
                    style="background: linear-gradient(135deg, #7c3aed, #db2777);">
                    {{ (leave.employee_name || leave.employee_username || '?')[0].toUpperCase() }}
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-800">{{ leave.employee_name || leave.employee_username }}</p>
                  </div>
                </div>
              </td>
              <td class="px-5 py-4">
                <span class="text-sm text-gray-600 capitalize">{{ leave.leave_type }}</span>
              </td>
              <td class="px-5 py-4 text-sm text-gray-600 whitespace-nowrap">
                {{ formatDate(leave.start_date) }}<br/>
                <span class="text-gray-400 text-xs">to {{ formatDate(leave.end_date) }}</span>
              </td>
              <td class="px-5 py-4 max-w-xs">
                <p class="text-sm text-gray-600 truncate" :title="leave.reason">{{ leave.reason }}</p>
                <p v-if="leave.comments" class="text-xs text-gray-400 italic mt-1">💬 {{ leave.comments }}</p>
              </td>
              <td class="px-5 py-4">
                <span class="text-xs font-bold px-3 py-1 rounded-full capitalize"
                  :class="{
                    'bg-yellow-100 text-yellow-700': leave.status === 'pending',
                    'bg-green-100 text-green-700': leave.status === 'approved',
                    'bg-red-100 text-red-700': leave.status === 'rejected'
                  }">
                  {{ leave.status }}
                </span>
              </td>
              <td class="px-5 py-4">
                <div v-if="leave.status === 'pending'" class="flex gap-2">
                  <button @click="approveLeave(leave.id)" :disabled="actionLoading === leave.id"
                    class="text-xs px-3 py-1.5 rounded-lg font-semibold bg-green-100 hover:bg-green-200 text-green-700 disabled:opacity-50">
                    ✓ Approve
                  </button>
                  <button @click="openRejectModal(leave)" :disabled="actionLoading === leave.id"
                    class="text-xs px-3 py-1.5 rounded-lg font-semibold bg-red-100 hover:bg-red-200 text-red-700 disabled:opacity-50">
                    ✕ Reject
                  </button>
                </div>
                <span v-else class="text-xs text-gray-400 italic">Reviewed</span>
              </td>
            </tr>
            <tr v-if="filteredLeaves.length === 0">
              <td colspan="6" class="py-12 text-center text-gray-400">
                <p class="text-3xl mb-2">📋</p>
                <p class="text-sm">No leave requests found</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Reject Modal -->
    <div v-if="showRejectModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 px-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
        <div class="px-6 py-4" style="background: linear-gradient(90deg, #7c3aed, #db2777);">
          <h3 class="text-white font-bold text-lg">Reject Leave Request</h3>
          <p class="text-purple-100 text-sm">{{ selectedLeave?.employee_name || selectedLeave?.employee_username }}</p>
        </div>
        <div class="p-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">Rejection Reason <span class="text-red-400">*</span></label>
          <textarea v-model="rejectComment" rows="3" placeholder="Explain why this leave is rejected..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400 mb-4">
          </textarea>
          <div class="flex justify-end gap-3">
            <button @click="showRejectModal = false"
              class="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-lg font-medium">
              Cancel
            </button>
            <button @click="rejectLeave" :disabled="rejecting || !rejectComment.trim()"
              class="px-4 py-2 text-sm text-white rounded-lg font-semibold disabled:opacity-50"
              style="background: linear-gradient(90deg, #7c3aed, #db2777);">
              {{ rejecting ? 'Rejecting...' : 'Confirm Reject' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <footer class="text-center py-6 text-xs text-gray-400 mt-4">
      © 2025 HuskyVoice.AI · Leave Management System
    </footer>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'EmployerDashboard',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user') || '{}'),
      leaves: [], loading: true, actionLoading: null,
      showRejectModal: false, rejecting: false, selectedLeave: null, rejectComment: '',
      activeFilter: 'all', flashMessage: '', flashType: 'success',
      filters: [
        { label: 'All', value: 'all' },
        { label: '🟡 Pending', value: 'pending' },
        { label: '✅ Approved', value: 'approved' },
        { label: '❌ Rejected', value: 'rejected' },
      ]
    }
  },
  computed: {
    filteredLeaves() {
      return this.activeFilter === 'all' ? this.leaves : this.leaves.filter(l => l.status === this.activeFilter)
    },
    stats() {
      return {
        total: this.leaves.length,
        pending: this.leaves.filter(l => l.status === 'pending').length,
        approved: this.leaves.filter(l => l.status === 'approved').length,
        rejected: this.leaves.filter(l => l.status === 'rejected').length,
      }
    }
  },
  mounted() { this.fetchLeaves() },
  methods: {
    formatDate(d) {
      if (!d) return '-'
      return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    },
    showFlash(msg, type = 'success') {
      this.flashMessage = msg; this.flashType = type
      setTimeout(() => { this.flashMessage = '' }, 3000)
    },
    async fetchLeaves() {
      this.loading = true
      try {
        const r = await api.get('/employer/leaves/')
        this.leaves = r.data
      } catch (err) {
        if (err.response?.status === 401) this.$router.push('/login')
        else if (err.response?.status === 403) this.showFlash('Access denied. Employer account required.', 'error')
        else this.showFlash('Failed to fetch leave requests.', 'error')
      } finally { this.loading = false }
    },
    async approveLeave(leaveId) {
      this.actionLoading = leaveId
      try {
        await api.patch(`/employer/leaves/${leaveId}/`, { status: 'approved' })
        this.showFlash('✅ Leave approved successfully.')
        await this.fetchLeaves()
      } catch { this.showFlash('Failed to approve leave.', 'error') }
      finally { this.actionLoading = null }
    },
    openRejectModal(leave) { this.selectedLeave = leave; this.rejectComment = ''; this.showRejectModal = true },
    async rejectLeave() {
      if (!this.rejectComment.trim()) return
      this.rejecting = true
      try {
        await api.patch(`/employer/leaves/${this.selectedLeave.id}/`, { status: 'rejected', comments: this.rejectComment })
        this.showFlash('Leave rejected.')
        this.showRejectModal = false
        await this.fetchLeaves()
      } catch { this.showFlash('Failed to reject leave.', 'error') }
      finally { this.rejecting = false }
    },
    logout() { localStorage.clear(); this.$router.push('/login') }
  }
}
</script>
