<template>
  <div>
    <el-card shadow="hover" style="margin-bottom: 20px">
      <template #header>
        <span style="font-weight: 600">用户信息</span>
      </template>
      <div v-if="currentUser">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="用户名">{{ currentUser.username }}</el-descriptions-item>
          <el-descriptions-item label="角色">
            <el-tag :type="roleTag(currentUser.role)" size="small">{{ roleLabel(currentUser.role) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="显示名称">{{ currentUser.display_name }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>

    <el-tabs v-model="activeTab">
      <!-- Station Management -->
      <el-tab-pane label="站点管理" name="stations">
        <el-card shadow="hover">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span style="font-weight: 600">监测站点管理</span>
              <el-button type="primary" size="small" @click="showStationDialog(null)" v-if="isAdmin">
                <el-icon style="margin-right: 4px"><Plus /></el-icon>
                新增站点
              </el-button>
            </div>
          </template>
          <el-table :data="stations" border stripe size="small" style="width: 100%">
            <el-table-column prop="station_id" label="编号" width="80" />
            <el-table-column prop="name" label="名称" width="140" />
            <el-table-column prop="location" label="位置" width="120" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="contact" label="联系人" width="160" />
            <el-table-column label="操作" width="160" v-if="isAdmin">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="showStationDialog(row)">编辑</el-button>
                <el-button type="danger" link size="small" @click="deleteStation(row.station_id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- Station Dialog -->
        <el-dialog v-model="stationDialog.visible" :title="stationDialog.isEdit ? '编辑站点' : '新增站点'" width="500px">
          <el-form ref="stationFormRef" :model="stationForm" label-width="80px">
            <el-form-item label="编号" prop="station_id" :rules="[{ required: true, message: '请输入站点编号' }]">
              <el-input v-model="stationForm.station_id" :disabled="stationDialog.isEdit" />
            </el-form-item>
            <el-form-item label="名称" prop="name">
              <el-input v-model="stationForm.name" />
            </el-form-item>
            <el-form-item label="位置" prop="location">
              <el-input v-model="stationForm.location" />
            </el-form-item>
            <el-form-item label="描述" prop="description">
              <el-input v-model="stationForm.description" type="textarea" :rows="2" />
            </el-form-item>
            <el-form-item label="联系人" prop="contact">
              <el-input v-model="stationForm.contact" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="stationDialog.visible = false">取消</el-button>
            <el-button type="primary" @click="saveStation" :loading="savingStation">保存</el-button>
          </template>
        </el-dialog>
      </el-tab-pane>

      <!-- User Management (admin only) -->
      <el-tab-pane label="用户管理" name="users" v-if="isAdmin">
        <el-card shadow="hover">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span style="font-weight: 600">用户账户管理</span>
              <el-button type="primary" size="small" @click="showUserDialog = true">
                <el-icon style="margin-right: 4px"><Plus /></el-icon>
                新增用户
              </el-button>
            </div>
          </template>
          <el-table :data="users" border stripe size="small" style="width: 100%">
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="display_name" label="显示名称" width="140" />
            <el-table-column prop="role" label="角色" width="100">
              <template #default="{ row }">
                <el-tag :type="roleTag(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="disabled" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.disabled ? 'danger' : 'success'" size="small">
                  {{ row.disabled ? '禁用' : '启用' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- User Dialog -->
        <el-dialog v-model="showUserDialog" title="新增用户" width="450px">
          <el-form ref="userFormRef" :model="userForm" label-width="80px">
            <el-form-item label="用户名" prop="username" :rules="[{ required: true, message: '请输入用户名' }]">
              <el-input v-model="userForm.username" />
            </el-form-item>
            <el-form-item label="密码" prop="password" :rules="[{ required: true, message: '请输入密码' }]">
              <el-input v-model="userForm.password" type="password" show-password />
            </el-form-item>
            <el-form-item label="显示名称" prop="display_name">
              <el-input v-model="userForm.display_name" />
            </el-form-item>
            <el-form-item label="角色" prop="role">
              <el-select v-model="userForm.role" style="width: 100%">
                <el-option label="管理员" value="admin" />
                <el-option label="编辑者" value="editor" />
                <el-option label="查看者" value="viewer" />
              </el-select>
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="showUserDialog = false">取消</el-button>
            <el-button type="primary" @click="createUser" :loading="creatingUser">创建</el-button>
          </template>
        </el-dialog>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import {
  getStations as apiGetStations, createStation, updateStation, deleteStation as apiDeleteStation,
  listUsers, registerUser, getCurrentUser,
} from '../api/index.js'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('stations')
const isAdmin = ref(false)
const currentUser = ref(null)

// Stations
const stations = ref([])
const stationDialog = ref({ visible: false, isEdit: false })
const stationForm = ref({ station_id: '', name: '', location: '', description: '', contact: '' })
const stationFormRef = ref(null)
const savingStation = ref(false)

// Users
const users = ref([])
const showUserDialog = ref(false)
const userForm = ref({ username: '', password: '', display_name: '', role: 'viewer' })
const userFormRef = ref(null)
const creatingUser = ref(false)

function roleTag(role) {
  return role === 'admin' ? 'danger' : role === 'editor' ? 'warning' : 'info'
}
function roleLabel(role) {
  return role === 'admin' ? '管理员' : role === 'editor' ? '编辑者' : '查看者'
}

async function loadCurrentUser() {
  try {
    const res = await getCurrentUser()
    currentUser.value = res.data
    isAdmin.value = res.data.role === 'admin'
  } catch (_) {
    currentUser.value = null
    isAdmin.value = false
  }
}

async function loadStations() {
  try {
    const res = await apiGetStations()
    stations.value = res.data.stations || []
  } catch (_) {}
}

async function loadUsers() {
  if (!isAdmin.value) return
  try {
    const res = await listUsers()
    users.value = res.data.users || []
  } catch (_) {}
}

function showStationDialog(row) {
  if (row) {
    stationForm.value = { ...row }
    stationDialog.value = { visible: true, isEdit: true }
  } else {
    stationForm.value = { station_id: '', name: '', location: '', description: '', contact: '' }
    stationDialog.value = { visible: true, isEdit: false }
  }
}

async function saveStation() {
  savingStation.value = true
  try {
    if (stationDialog.value.isEdit) {
      await updateStation(stationForm.value.station_id, stationForm.value)
      ElMessage.success('站点已更新')
    } else {
      await createStation(stationForm.value)
      ElMessage.success('站点已创建')
    }
    stationDialog.value.visible = false
    await loadStations()
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
  }
  savingStation.value = false
}

async function deleteStation(id) {
  try {
    await ElMessageBox.confirm(`确定删除站点 ${id}？`, '警告', { type: 'warning' })
    await apiDeleteStation(id)
    ElMessage.success('站点已删除')
    await loadStations()
  } catch (_) {}
}

async function createUser() {
  creatingUser.value = true
  try {
    await registerUser(userForm.value.username, userForm.value.password, userForm.value.role, userForm.value.display_name)
    ElMessage.success('用户已创建')
    showUserDialog.value = false
    await loadUsers()
  } catch (e) {
    ElMessage.error('创建失败: ' + (e.response?.data?.detail || e.message))
  }
  creatingUser.value = false
}

onMounted(() => {
  loadCurrentUser()
  loadStations()
  loadUsers()
})
</script>
