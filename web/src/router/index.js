import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import DataManagement from '../views/DataManagement.vue'
import Prediction from '../views/Prediction.vue'
import AlertManagement from '../views/AlertManagement.vue'
import Login from '../views/Login.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { title: '首页看板' },
  },
  {
    path: '/data',
    name: 'DataManagement',
    component: DataManagement,
    meta: { title: '数据管理' },
  },
  {
    path: '/predict',
    name: 'Prediction',
    component: Prediction,
    meta: { title: '水质预测' },
  },
  {
    path: '/alert',
    name: 'AlertManagement',
    component: AlertManagement,
    meta: { title: '告警管理' },
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录' },
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { title: '后台管理', requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Simple route guard for auth-required pages
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    if (!token) {
      next({ path: '/login', query: { redirect: to.fullPath } })
      return
    }
  }
  next()
})

export default router
