<template>
  <div>
    <!-- Stats Cards -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #e6f7ff">
              <el-icon size="28" color="#1890ff"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_records }}</div>
              <div class="stat-label">总记录数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #f6ffed">
              <el-icon size="28" color="#52c41a"><Location /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.station_count }}</div>
              <div class="stat-label">监测站点</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #fff7e6">
              <el-icon size="28" color="#fa8c16"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.model_status }}</div>
              <div class="stat-label">模型状态</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #fce4ec">
              <el-icon size="28" color="#f56c6c"><DataAnalysis /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.cleaned_records || 0 }}</div>
              <div class="stat-label">清洗后记录</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Station Cards -->
    <el-card shadow="hover" style="margin-bottom: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="font-weight: 600">站点最新数据</span>
          <el-tag type="info" size="small">数据更新时间: {{ stats.last_update || '暂无' }}</el-tag>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="8" v-for="station in stations" :key="station.id">
          <el-card shadow="never" style="border: 1px solid #ebeef5">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px">
              <span style="font-weight: 600; font-size: 15px">{{ station.id }}</span>
              <el-tag :type="station.grade_tag" size="small" effect="dark">{{ station.grade }}</el-tag>
            </div>
            <div class="indicator-grid">
              <div class="indicator-item" v-for="ind in station.indicators" :key="ind.name">
                <span class="indicator-label">{{ ind.label }}</span>
                <span class="indicator-value" :style="{ color: ind.color }">{{ ind.value }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8" v-if="stations.length === 0">
          <el-empty description="暂无站点数据，请先上传数据" />
        </el-col>
      </el-row>
    </el-card>

    <!-- Quick Actions -->
    <el-card shadow="hover">
      <template #header>
        <span style="font-weight: 600">快速操作</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-button type="primary" size="large" style="width: 100%" @click="$router.push('/data')">
            <el-icon style="margin-right: 6px"><Upload /></el-icon>
            数据管理
          </el-button>
        </el-col>
        <el-col :span="8">
          <el-button type="success" size="large" style="width: 100%" @click="$router.push('/predict')">
            <el-icon style="margin-right: 6px"><TrendCharts /></el-icon>
            预测分析
          </el-button>
        </el-col>
        <el-col :span="8">
          <el-button type="warning" size="large" style="width: 100%" @click="refreshAll">
            <el-icon style="margin-right: 6px"><Refresh /></el-icon>
            刷新数据
          </el-button>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDataSummary, getStations, getDataInfo, getModelInfo } from '../api/index.js'

const stats = ref({
  total_records: '--',
  station_count: '--',
  model_status: '--',
  cleaned_records: '--',
  last_update: '--',
})

const stations = ref([])

const indicatorConfig = {
  ph: { label: 'pH', unit: '', color: '#409EFF' },
  do: { label: 'DO', unit: 'mg/L', color: '#67C23A' },
  nh3n: { label: 'NH3N', unit: 'mg/L', color: '#E6A23C' },
  turbidity: { label: '浊度', unit: 'NTU', color: '#F56C6C' },
  temperature: { label: '水温', unit: '°C', color: '#909399' },
  cod: { label: 'COD', unit: 'mg/L', color: '#9B59B6' },
  total_phosphorus: { label: '总磷', unit: 'mg/L', color: '#1ABC9C' },
}

function getGradeTag(ph, doVal, nh3n) {
  if (ph >= 6.5 && ph <= 8.5 && doVal >= 5 && nh3n <= 0.5) return { grade: 'I~II类', tag: 'success' }
  if (ph >= 6 && ph <= 9 && doVal >= 3 && nh3n <= 1.0) return { grade: 'III类', tag: 'warning' }
  return { grade: 'IV~V类', tag: 'danger' }
}

async function loadData() {
  try {
    const [summaryRes, infoRes, modelRes] = await Promise.all([
      getDataSummary().catch(() => ({ data: {} })),
      getDataInfo().catch(() => ({ data: {} })),
      getModelInfo().catch(() => ({ data: { status: 'not_ready' } })),
    ])

    const summary = summaryRes.data

    stats.value = {
      total_records: summary.total_records || '--',
      station_count: (summary.station_ids || []).length || '--',
      model_status: modelRes.data.status === 'not_ready' ? '未训练' : '已就绪',
      cleaned_records: summary.total_cleaned || '--',
      last_update: summary.latest_time || '--',
    }

    // Build station cards
    const stationIds = summary.station_ids || []
    stations.value = stationIds.map((sid) => {
      const indicators = []
      for (const [key, cfg] of Object.entries(indicatorConfig)) {
        if (summary.latest_values && summary.latest_values[sid] && summary.latest_values[sid][key] !== undefined) {
          indicators.push({
            name: key,
            label: cfg.label,
            value: summary.latest_values[sid][key].toFixed(2) + (cfg.unit ? ' ' + cfg.unit : ''),
            color: cfg.color,
          })
        }
      }
      const ph = summary.latest_values?.[sid]?.ph || 7
      const doV = summary.latest_values?.[sid]?.do || 5
      const nh3n = summary.latest_values?.[sid]?.nh3n || 0.3
      return { id: sid, ...getGradeTag(ph, doV, nh3n), indicators }
    })
  } catch (e) {
    console.error('Failed to load dashboard:', e)
  }
}

function refreshAll() {
  loadData()
}

onMounted(loadData)
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
.indicator-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}
.indicator-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 2px 0;
}
.indicator-label {
  color: #909399;
}
.indicator-value {
  font-weight: 600;
}
</style>
