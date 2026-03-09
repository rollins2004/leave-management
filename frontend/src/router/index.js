import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/Login.vue'
import Register from '../components/Register.vue'
import EmployeeDashboard from '../components/EmployeeDashboard.vue'
import EmployerDashboard from '../components/EmployerDashboard.vue'

const routes = [
  { path: '/', redirect: '/login' },
  {
    path: '/login',
    component: Login,
    meta: { guest: true }
  },
  {
    path: '/register',
    component: Register,
    meta: { guest: true }
  },
  {
    path: '/employee/dashboard',
    component: EmployeeDashboard,
    meta: { requiresAuth: true, role: 'employee' }
  },
  {
    path: '/employer/dashboard',
    component: EmployerDashboard,
    meta: { requiresAuth: true, role: 'employer' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard - protect routes and redirect based on role
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }

  if (to.meta.guest && token) {
    // Already logged in, redirect to correct dashboard
    const role = user.role || 'employee'
    return next(role === 'employer' ? '/employer/dashboard' : '/employee/dashboard')
  }

  next()
})

export default router
