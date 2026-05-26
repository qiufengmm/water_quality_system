<template>
  <div>
    <!-- Alert Rules -->
    <el-card shadow="hover" style="margin-bottom: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="font-weight: 600">告警规则配置</span>
          <el-button type="primary" size="small" @click="saveRules" :loading="savingRules">
            <el-icon style="margin-right: 4px"><Check /></el-icon>
            保存规则
          </el-button>
        </div>
      </template>
      <el-table :data="rules" border stripe size="small" style="width: 100%">
        <el-table-column prop="label" label="指标" width="140" />
        <el-table-column prop="operator" label="运算符" width="80">
          <template #default="{ row }">
            <el-select v-model="row.operator" size="small" style="width: 70px">
              <el-option label=">" value=">" />
              <el-option label="<" value="<" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column prop="threshold" label="阈值" width="120">
          <template #default="{ row }">
            <el-input-number v-model="row.threshold" size="small" :min="0" :step="0.1" :precision="2" style="width: 100px" />
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="严重级别" width="120">
          <template #default="{ row }">
            <el-select v-model="row.severity" size="small">
              <el-option label="信息" value="info" />
              <el-option label="警告" value="warning" />
              <el-option label="严重" value="critical" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="启用" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Alert Check -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #fce4ec">
              <el-icon size="28" color="#f56c6c"><WarningFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value" style="color: #f56c6c">{{ stats.critical }}</div>
              <div class="stat-label">严重告警</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #fff7e6">
              <el-icon size="28" color="#fa8c16"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value" style="color: #fa8c16">{{ stats.warning }}</div>
              <div class="stat-label">警告</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #e6f7ff">
              <el-icon size="28" color="#1890ff"><InfoFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value" style="color: #1890ff">{{ stats.info }}</div>
              <div class="stat-label">信息</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #f0f2f5">
              <el-icon size="28" color="#606266"><List /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total }}</div>
              <div class="stat-label">告警总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Check Button + History -->
    <el-card shadow="hover" style="margin-bottom: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="font-weight: 600">告警检查</span>
          <div>
            <el-button type="danger" @click="runCheck" :loading="checking">
              <el-icon style="margin-right: 4px"><Search /></el-icon>
              执行告警检查
            </el-button>
            <el-button type="danger" plain @click="clearHistory" style="margin-left: 8px">
              <el-icon style="margin-right: 4px"><Delete /></el-icon>
              清空历史
            </el-button>
          </div>
        </div>
      </template>

      <!-- Check results summary -->
      <el-alert
        v-if="checkResult"
        :title="checkResultMsg"
        :type="checkResultType"
        show-icon
        style="margin-bottom: 12px"
        closable
      />
    </el-card>

    <!-- Alert History -->
    <el-card shadow="hover">
      <template #header>
        <span style="font-weight: 600">告警历史记录</span>
      </template>
      <el-table :data="historyRecords" border stripe size="small" style="width: 100%" v-loading="loading">
        <el-table-column prop="timestamp" label="时间" width="160" />
        <el-table-column prop="station_id" label="站点" width="80" />
        <el-table-column prop="indicator" label="指标" width="100" />
        <el-table-column prop="value" label="数值" width="80" />
        <el-table-column prop="rule" label="规则" width="160" />
        <el-table-column prop="severity" label="级别" width="80">
          <template #default="{ row }">
            <el-tag :type="severityTag(row.severity)" size="small" effect="dark">
              {{ severityLabel(row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'danger' : 'info'" size="small">
              {{ row.status === 'active' ? '活跃' : '已处理' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div style="display: flex; justify-content: center; margin-top: 16px">
        <el-pagination
          v-model:current-page="historyPage"
          :page-size="historyPageSize"
          :total="historyTotal"
          layout="prev, pager, next"
          @current-change="loadHistory"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  getAlertRules, updateAlertRules, checkAlerts,
  getAlertHistory, clearAlertHistory,
} from '../api/index.js'
import { ElMessage, ElMessageBox } from 'element-plus'

const rules = ref([])
const savingRules = ref(false)
const checking = ref(false)
const loading = ref(false)
const checkResult = ref(false)
const checkResultMsg = ref('')
const checkResultType = ref('success')

const stats = ref({ critical: 0, warning: 0, info: 0, total: 0 })

const historyRecords = ref([])
const historyPage = ref(1)
const historyPageSize = ref(20)
const historyTotal = ref(0)

function severityTag(s) {
  return s === 'critical' ? 'danger' : s === 'warning' ? 'warning' : 'info'
}
function severityLabel(s) {
  return s === 'critical' ? '严重' : s === 'warning' ? '警告' : '信息'
}

async function loadRules() {
  try {
    const res = await getAlertRules()
    rules.value = res.data.rules || []
  } catch (_) {}
}

async function saveRules() {
  savingRules.value = true
  try {
    await updateAlertRules(rules.value)
    ElMessage.success('规则已保存')
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
  }
  savingRules.value = false
}

async function runCheck() {
  checking.value = true
  try {
    const res = await checkAlerts()
    const d = res.data
    checkResult.value = true
    checkResultMsg.value = `检查完成: ${d.checked_records} 条记录，触发 ${d.alerts_triggered} 条告警`
    checkResultType.value = d.alerts_triggered > 0 ? 'warning' : 'success'
    if (d.alerts_triggered > 0) {
      stats.value = {
        critical: d.severity_summary?.critical || 0,
        warning: d.severity_summary?.warning || 0,
        info: d.severity_summary?.info || 0,
        total: d.alerts_triggered,
      }
    }
    await loadHistory()
  } catch (e) {
    ElMessage.error('检查失败: ' + (e.response?.data?.detail || e.message))
  }
  checking.value = false
}

async function loadHistory() {
  loading.value = true
  try {
    const res = await getAlertHistory(historyPage.value, historyPageSize.value)
    const d = res.data
    historyRecords.value = d.records || []
    historyTotal.value = d.total || 0
  } catch (_) {
    historyRecords.value = []
    historyTotal.value = 0
  }
  loading.value = false
}

async function clearHistory() {
  try {
    await ElMessageBox.confirm('确定清空所有告警历史记录？', '警告', { type: 'warning' })
    await clearAlertHistory()
    stats.value = { critical: 0, warning: 0, info: 0, total: 0 }
    await loadHistory()
    ElMessage.success('历史已清空')
  } catch (_) {}
}

onMounted(() => {
  loadRules()
  loadHistory()
})
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
}
.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.stat-info {
  flex: 1;
}
.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}
.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}
</style>
