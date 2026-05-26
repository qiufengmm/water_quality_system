import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import DataManagement from '../views/DataManagement.vue'
import Prediction from '../views/Prediction.vue'

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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
