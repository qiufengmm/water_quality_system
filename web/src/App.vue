<template>
  <el-container style="min-height: 100vh">
    <el-aside width="220px" style="background: #304156">
      <div class="sidebar-header">
        <el-icon size="24" color="#409EFF"><Monitor /></el-icon>
        <span class="sidebar-title">水质监测系统</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/">
          <el-icon><Monitor /></el-icon>
          <span>首页看板</span>
        </el-menu-item>
        <el-menu-item index="/data">
          <el-icon><DataBoard /></el-icon>
          <span>数据管理</span>
        </el-menu-item>
        <el-menu-item index="/predict">
          <el-icon><TrendCharts /></el-icon>
          <span>水质预测</span>
        </el-menu-item>
        <el-menu-item index="/alert">
          <el-icon><WarningFilled /></el-icon>
          <span>告警管理</span>
        </el-menu-item>
        <el-menu-item index="/admin">
          <el-icon><Setting /></el-icon>
          <span>后台管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background: #fff; border-bottom: 1px solid #e6e6e6; display: flex; align-items: center; justify-content: space-between">
        <div class="header-left">
          <h2 style="margin: 0; font-size: 18px; font-weight: 500; color: #303133">{{ $route.meta.title }}</h2>
        </div>
        <div class="header-right" style="display: flex; align-items: center; gap: 12px">
          <span style="color: #909399; font-size: 13px">基于大数据与机器学习的水质监测与预测系统</span>
          <template v-if="loggedIn">
            <el-dropdown @command="handleCommand">
              <span style="cursor: pointer; display: flex; align-items: center; gap: 4px; color: #606266">
                <el-icon><UserFilled /></el-icon>
                {{ displayName }}
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="admin" v-if="role === 'admin'">后台管理</el-dropdown-item>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button size="small" @click="$router.push('/login')">登录</el-button>
          </template>
        </div>
      </el-header>
      <el-main style="background: #f0f2f5; padding: 20px">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Monitor, DataBoard, TrendCharts, WarningFilled,
  Setting, UserFilled,
} from '@element-plus/icons-vue'

const router = useRouter()
const loggedIn = ref(false)
const displayName = ref('')
const role = ref('')

function updateAuthState() {
  const token = localStorage.getItem('token')
  loggedIn.value = !!token
  displayName.value = localStorage.getItem('display_name') || localStorage.getItem('username') || ''
  role.value = localStorage.getItem('role') || ''
}

function handleCommand(command) {
  if (command === 'logout') {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('role')
    localStorage.removeItem('display_name')
    updateAuthState()
    router.push('/')
  } else if (command === 'admin') {
    router.push('/admin')
  }
}

onMounted(updateAuthState)
</script>

<style>
body {
  margin: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.sidebar-title {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
}
.el-menu {
  border-right: none;
}
</style>
