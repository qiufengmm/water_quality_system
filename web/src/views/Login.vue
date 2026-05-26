<template>
  <div class="login-container">
    <el-card class="login-card" shadow="always">
      <div style="text-align: center; margin-bottom: 24px">
        <el-icon size="48" color="#409EFF"><Monitor /></el-icon>
        <h2 style="margin: 12px 0 4px; font-size: 20px; color: #303133">水质监测系统</h2>
        <p style="margin: 0; color: #909399; font-size: 13px">用户登录</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="0" size="large">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" style="width: 100%" @click="handleLogin" :loading="loading">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <div style="text-align: center; margin-top: 12px">
        <el-button type="text" size="small" @click="$router.push('/')">
          返回首页
        </el-button>
      </div>
      <div style="margin-top: 16px; padding: 12px; background: #f5f7fa; border-radius: 6px; font-size: 12px; color: #909399">
        <p style="margin: 0 0 4px">演示账号：</p>
        <p style="margin: 0">管理员：admin / admin123</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { login } from '../api/index.js'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await login(form.username, form.password)
    const d = res.data
    // Store token
    localStorage.setItem('token', d.access_token)
    localStorage.setItem('username', d.username)
    localStorage.setItem('role', d.role)
    localStorage.setItem('display_name', d.display_name)
    ElMessage.success(`欢迎回来，${d.display_name || d.username}`)
    // Redirect to previous page or admin
    const redirect = router.currentRoute.value.query?.redirect || '/'
    router.push(redirect)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '登录失败')
  }
  loading.value = false
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
}
.login-card {
  width: 400px;
}
</style>
