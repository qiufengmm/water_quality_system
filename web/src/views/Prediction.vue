<template>
  <div>
    <!-- Control Panel -->
    <el-card shadow="hover" style="margin-bottom: 20px">
      <template #header>
        <span style="font-weight: 600">预测控制</span>
      </template>
      <el-row :gutter="20" align="middle">
        <el-col :span="6">
          <div style="margin-bottom: 4px; font-size: 13px; color: #606266">选择站点</div>
          <el-select v-model="stationId" style="width: 100%">
            <el-option v-for="s in stations" :key="s.station_id" :label="s.name || s.station_id" :value="s.station_id" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <div style="margin-bottom: 4px; font-size: 13px; color: #606266">预测天数: {{ days }} 天</div>
          <el-slider v-model="days" :min="1" :max="30" :step="1" show-stops />
        </el-col>
        <el-col :span="10" style="display: flex; gap: 12px; align-items: flex-end">
          <el-button type="warning" @click="trainModelAction" :loading="training">
            <el-icon style="margin-right: 4px"><Cpu /></el-icon>
            训练模型
          </el-button>
          <el-button type="primary" @click="predictAction" :loading="predicting" :disabled="!modelReady">
            <el-icon style="margin-right: 4px"><TrendCharts /></el-icon>
            开始预测
          </el-button>
          <el-tag v-if="modelReady" type="success" effect="dark">模型就绪</el-tag>
          <el-tag v-else type="info" effect="dark">模型待训练</el-tag>
        </el-col>
      </el-row>
    </el-card>

    <!-- Prediction Results -->
    <el-card shadow="hover" v-if="hasResult">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="font-weight: 600">预测结果 — {{ result.station_id }}</span>
          <el-tag type="success">置信度: {{ (result.confidence * 100).toFixed(1) }}%</el-tag>
        </div>
      </template>

      <!-- Charts -->
      <div style="margin-bottom: 20px">
        <el-row :gutter="16">
          <el-col :span="12" v-for="ind in chartIndicators" :key="ind.key" style="margin-bottom: 16px">
            <div style="border: 1px solid #ebeef5; border-radius: 8px; padding: 12px">
              <div style="font-weight: 600; margin-bottom: 8px; font-size: 14px">{{ ind.label }}</div>
              <div :ref="el => setChartRef(ind.key, el)" style="height: 220px"></div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Detail Table -->
      <el-table :data="detailRows" border stripe size="small" style="width: 100%">
        <el-table-column type="index" label="天" width="60" />
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="ph" label="pH" width="100" />
        <el-table-column prop="do" label="DO" width="100" />
        <el-table-column prop="nh3n" label="NH3N" width="100" />
        <el-table-column prop="turbidity" label="浊度" width="100" />
        <el-table-column prop="temperature" label="水温" width="100" />
        <el-table-column prop="cod" label="COD" width="100" />
        <el-table-column prop="total_phosphorus" label="总磷" width="100" />
      </el-table>
    </el-card>

    <!-- Empty state -->
    <el-card shadow="hover" v-else>
      <el-empty description="选择站点和天数后点击「开始预测」查看结果" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { trainModel, predictBatch, getModelInfo, getStations, getDataSummary } from '../api/index.js'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const stationId = ref('ST001')
const days = ref(7)
const stations = ref([])
const training = ref(false)
const predicting = ref(false)
const modelReady = ref(false)
const hasResult = ref(false)
const result = ref({ station_id: '', predictions: {}, dates: [], confidence: 0 })

const chartRefs = {}
const chartInstances = {}

const indicatorMeta = [
  { key: 'ph', label: 'pH', color: '#409EFF' },
  { key: 'do', label: 'DO', color: '#67C23A' },
  { key: 'nh3n', label: 'NH3N', color: '#E6A23C' },
  { key: 'turbidity', label: '浊度', color: '#F56C6C' },
  { key: 'temperature', label: '水温', color: '#909399' },
  { key: 'cod', label: 'COD', color: '#9B59B6' },
  { key: 'total_phosphorus', label: '总磷', color: '#1ABC9C' },
]

const chartIndicators = ref([])

function setChartRef(key, el) {
  if (el) chartRefs[key] = el
}

function renderCharts() {
  nextTick(() => {
    for (const ind of chartIndicators.value) {
      if (chartInstances[ind.key]) chartInstances[ind.key].dispose()
      const el = chartRefs[ind.key]
      if (!el) continue

      const chart = echarts.init(el)
      chartInstances[ind.key] = chart

      const values = result.value.predictions[ind.key] || []
      const dates = result.value.dates || []

      chart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '8%', right: '8%', top: 15, bottom: 25, containLabel: true },
        xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45, fontSize: 10 } },
        yAxis: { type: 'value', name: ind.label },
        series: [{
          type: 'line',
          data: values,
          smooth: true,
          lineStyle: { color: ind.color, width: 2 },
          itemStyle: { color: ind.color },
          areaStyle: { color: echarts.graphic?.LinearGradient?.(0, 0, 0, 1, [
            { offset: 0, color: ind.color + '40' },
            { offset: 1, color: ind.color + '05' },
          ]) || { opacity: 0.1 } },
          symbol: 'circle',
          symbolSize: 6,
        }],
      })
    }
  })
}

const detailRows = ref([])

function buildDetailTable() {
  const rows = []
  const dates = result.value.dates || []
  const preds = result.value.predictions || {}
  for (let i = 0; i < dates.length; i++) {
    const row = { date: dates[i] }
    for (const ind of indicatorMeta) {
      row[ind.key] = (preds[ind.key]?.[i] ?? '-').toFixed?.(2) ?? preds[ind.key]?.[i] ?? '-'
    }
    rows.push(row)
  }
  detailRows.value = rows
}

async function checkModel() {
  try {
    const res = await getModelInfo()
    modelReady.value = res.data.is_trained === true
  } catch (_) {
    modelReady.value = false
  }
}

async function trainModelAction() {
  training.value = true
  try {
    const res = await trainModel()
    ElMessage.success(`模型训练完成! 平均R²: ${res.data.avg_r2?.toFixed?.(4) || 'N/A'}`)
    modelReady.value = true
  } catch (e) {
    ElMessage.error('训练失败: ' + (e.response?.data?.detail || e.message))
  }
  training.value = false
}

async function predictAction() {
  predicting.value = true
  try {
    const res = await predictBatch(stationId.value, days.value)
    result.value = res.data

    // Show only indicators that have predictions
    chartIndicators.value = indicatorMeta.filter(
      (ind) => result.value.predictions && result.value.predictions[ind.key]
    )

    hasResult.value = true
    ElMessage.success(result.value.message || '预测完成')
    buildDetailTable()

    nextTick(() => renderCharts())
  } catch (e) {
    ElMessage.error('预测失败: ' + (e.response?.data?.detail || e.message))
  }
  predicting.value = false
}

async function loadStations() {
  try {
    const res = await getStations()
    if (res.data.stations?.length) stations.value = res.data.stations
  } catch (_) {}
}

onMounted(() => {
  checkModel()
  loadStations()
})

onUnmounted(() => {
  for (const inst of Object.values(chartInstances)) inst.dispose()
})
</script>
