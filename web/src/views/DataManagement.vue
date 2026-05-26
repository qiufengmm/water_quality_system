<template>
  <div>
    <el-card shadow="hover" style="margin-bottom: 20px">
      <template #header>
        <span style="font-weight: 600">数据上传</span>
      </template>
      <el-row :gutter="20" align="middle">
        <el-col :span="12">
          <el-upload
            drag
            action="/api/data/upload"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            accept=".csv,.xlsx,.xls"
          >
            <el-icon size="48" color="#409EFF"><UploadFilled /></el-icon>
            <div style="margin-top: 8px; font-size: 14px; color: #606266">
              拖拽 CSV/Excel 文件到此处，或 <em style="color: #409EFF">点击上传</em>
            </div>
            <template #tip>
              <div style="font-size: 12px; color: #909399; margin-top: 4px">
                支持 .csv / .xlsx / .xls 格式
              </div>
            </template>
          </el-upload>
        </el-col>
        <el-col :span="12">
          <div style="display: flex; flex-direction: column; gap: 12px">
            <el-button type="primary" @click="simulateData" :loading="simulating">
              <el-icon style="margin-right: 4px"><Cpu /></el-icon>
              生成模拟数据
            </el-button>
            <el-button type="danger" @click="confirmDeleteRaw" :disabled="!hasRaw">
              <el-icon style="margin-right: 4px"><Delete /></el-icon>
              清空原始数据
            </el-button>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="hover" style="margin-bottom: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="font-weight: 600">数据清洗</span>
          <div>
            <el-button type="success" @click="doClean" :loading="cleaning" :disabled="!hasRaw">
              <el-icon style="margin-right: 4px"><Brush /></el-icon>
              执行清洗
            </el-button>
            <el-button type="danger" @click="confirmDeleteCleaned" :disabled="!hasCleaned" style="margin-left: 8px">
              <el-icon style="margin-right: 4px"><Delete /></el-icon>
              清空清洗数据
            </el-button>
          </div>
        </div>
      </template>
      <el-table :data="cleanReport.rows" v-if="cleanReport.show" style="margin-bottom: 12px" border>
        <el-table-column prop="item" label="项目" width="150" />
        <el-table-column prop="before" label="清洗前" />
        <el-table-column prop="after" label="清洗后" />
      </el-table>
    </el-card>

    <el-card shadow="hover">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="font-weight: 600">数据浏览</span>
          <el-radio-group v-model="dataTab" size="small">
            <el-radio-button value="raw">原始数据</el-radio-button>
            <el-radio-button value="cleaned">清洗后数据</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <el-table :data="tableData" v-loading="loading" border stripe style="width: 100%">
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="station_id" label="站点" width="80" />
        <el-table-column prop="collection_time" label="采集时间" width="160" />
        <el-table-column prop="ph" label="pH" width="80" />
        <el-table-column prop="do" label="DO" width="80" />
        <el-table-column prop="nh3n" label="NH3N" width="80" />
        <el-table-column prop="turbidity" label="浊度" width="80" />
        <el-table-column prop="temperature" label="水温" width="80" />
        <el-table-column prop="cod" label="COD" width="80" />
        <el-table-column prop="total_phosphorus" label="总磷" width="80" />
      </el-table>
      <div style="display: flex; justify-content: center; margin-top: 16px">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="loadTableData"
        />
      </div>
    </el-card>

    <!-- Upload success dialog -->
    <el-dialog v-model="uploadDialog.visible" title="上传结果" width="400px">
      <p>成功导入 <strong>{{ uploadDialog.count }}</strong> 条记录</p>
      <p>检测到列: {{ uploadDialog.columns }}</p>
      <template #footer>
        <el-button type="primary" @click="uploadDialog.visible = false; refreshAll()">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import {
  getRawData, getCleanedData, getDataInfo,
  simulateData as apiSimulate, cleanData as apiClean,
  deleteRawData, deleteCleanedData,
} from '../api/index.js'
import { ElMessage, ElMessageBox } from 'element-plus'

const dataTab = ref('raw')
const loading = ref(false)
const tableData = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const hasRaw = ref(false)
const hasCleaned = ref(false)
const simulating = ref(false)
const cleaning = ref(false)

const cleanReport = ref({ show: false, rows: [] })

const uploadDialog = ref({ visible: false, count: 0, columns: '' })

async function loadTableData() {
  loading.value = true
  try {
    let res
    if (dataTab.value === 'raw') {
      res = await getRawData(page.value, pageSize.value)
    } else {
      res = await getCleanedData(page.value, pageSize.value)
    }
    const d = res.data
    tableData.value = d.records || d.data || []
    total.value = d.total || tableData.value.length
  } catch (e) {
    tableData.value = []
    total.value = 0
  }
  loading.value = false
}

async function refreshInfo() {
  try {
    const res = await getDataInfo()
    hasRaw.value = res.data.has_raw
    hasCleaned.value = res.data.has_cleaned
  } catch (_) {}
}

watch(dataTab, () => {
  page.value = 1
  loadTableData()
})

function handleUploadSuccess(res) {
  uploadDialog.value = {
    visible: true,
    count: res.records_loaded || 0,
    columns: (res.columns_detected || []).join(', '),
  }
  refreshInfo()
  loadTableData()
}

function handleUploadError() {
  ElMessage.error('上传失败')
}

async function simulateData() {
  simulating.value = true
  try {
    const res = await apiSimulate('ST001', 24, 60)
    ElMessage.success(`生成了 ${res.data.records_loaded || 12} 条模拟数据`)
    refreshInfo()
    loadTableData()
  } catch (e) {
    ElMessage.error('生成模拟数据失败')
  }
  simulating.value = false
}

async function doClean() {
  cleaning.value = true
  try {
    const res = await apiClean({ handle_missing: 'interpolate', outlier_method: 'iqr', outlier_threshold: 1.5 })
    const d = res.data
    cleanReport.value = {
      show: true,
      rows: [
        { item: '总记录数', before: d.total_records, after: d.records_after },
        { item: '重复记录', before: d.duplicates_removed, after: '-' },
        { item: '异常值', before: d.outliers_removed, after: '-' },
        { item: '清洗后记录', before: '-', after: d.records_after },
      ],
    }
    ElMessage.success(`清洗完成: ${d.total_records} → ${d.records_after} 条`)
    refreshInfo()
    loadTableData()
  } catch (e) {
    ElMessage.error('清洗失败: ' + (e.response?.data?.detail || e.message))
  }
  cleaning.value = false
}

function confirmDeleteRaw() {
  ElMessageBox.confirm('确定清空所有原始数据？', '警告', { type: 'warning' }).then(async () => {
    await deleteRawData()
    ElMessage.success('已清空')
    refreshInfo()
    loadTableData()
  }).catch(() => {})
}

function confirmDeleteCleaned() {
  ElMessageBox.confirm('确定清空所有清洗后数据？', '警告', { type: 'warning' }).then(async () => {
    await deleteCleanedData()
    ElMessage.success('已清空')
    refreshInfo()
    loadTableData()
  }).catch(() => {})
}

function refreshAll() {
  refreshInfo()
  loadTableData()
}

onMounted(() => {
  refreshInfo()
  loadTableData()
})
</script>
