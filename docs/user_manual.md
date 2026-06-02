# 水质监测与预测系统 — 用户说明书

> 基于大数据与机器学习的水质监测与预测系统
> 版本 1.0.0 | 第2组

---

## 目录

1. [系统概述](#1-系统概述)
2. [环境准备与启动](#2-环境准备与启动)
3. [数据采集](#3-数据采集)
4. [数据查询与统计](#4-数据查询与统计)
5. [数据清洗](#5-数据清洗)
6. [ML 预测模型](#6-ml-预测模型)
7. [告警管理](#7-告警管理)
8. [后台管理](#8-后台管理)
9. [数据导出](#9-数据导出)
10. [Web 前端操作指南](#10-web-前端操作指南)
11. [常见问题](#11-常见问题)

---

## 1. 系统概述

### 1.1 功能架构

```
┌────────────────────────────────────────────────────────┐
│                    前端页面 (Vue 3)                      │
│  看板  │  数据管理  │  水质预测  │  告警管理  │  后台管理  │
└──────────────────────┬─────────────────────────────────┘
                       │ REST API (JSON)
┌──────────────────────┴─────────────────────────────────┐
│                   后端 API (FastAPI)                     │
│  ┌────────┐ ┌────────┐ ┌───────┐ ┌────────┐ ┌───────┐ │
│  │数据采集 │ │数据清洗 │ │ML预测 │ │告警引擎│ │后台管理│ │
│  │CSV/模拟 │ │去重/插值│ │XGBoost│ │GB3838 │ │JWT认证│ │
│  │手动录入 │ │IQR/Z   │ │7指标  │ │12规则  │ │站点管理│ │
│  └────────┘ └────────┘ └───────┘ └────────┘ └───────┘ │
└──────────────────────┬─────────────────────────────────┘
                       │ 文件存储
┌──────────────────────┴─────────────────────────────────┐
│     数据文件 (CSV)  │  用户/站点配置 (JSON)  │  模型文件   │
└────────────────────────────────────────────────────────┘
```

### 1.2 默认账号

| 用户名 | 密码 | 角色 | 权限 |
|--------|------|------|------|
| `admin` | `admin123` | 管理员 | 全部权限（管理站点、用户、数据） |

### 1.3 默认站点

| 站点 ID | 名称 | 说明 |
|---------|------|------|
| ST001 | 上游监测站 | 河流上游监测点 |
| ST002 | 中游监测站 | 河流中游监测点 |
| ST003 | 下游监测站 | 河流下游监测点 |

---

## 2. 环境准备与启动

### 2.1 环境要求

- Python 3.9+
- Node.js 18+

### 2.2 安装依赖

```bash
# 后端依赖
cd C:\Users\qiufengm\Desktop\智慧水利应用\water_quality_system
pip install -r requirements.txt

# 前端依赖
cd web
npm install
```

### 2.3 启动服务

**启动后端（终端 1）：**
```bash
cd C:\Users\qiufengm\Desktop\智慧水利应用\water_quality_system
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**启动前端（终端 2）：**
```bash
cd C:\Users\qiufengm\Desktop\智慧水利应用\water_quality_system\web
npm run dev
```

### 2.4 访问地址

| 地址 | 说明 |
|------|------|
| http://localhost:5173 | 前端页面 |
| http://localhost:8000 | 后端 API |
| http://localhost:8000/docs | Swagger API 文档 |
| http://localhost:8000/health | 健康检查 |

---

## 3. 数据采集

系统提供 **三种数据录入方式**。使用前请确保后端服务已启动。

### 3.1 方式一：上传 CSV/Excel 文件（推荐）

将本地的 CSV 或 Excel 文件上传到系统。

**命令格式：**
```bash
curl -X POST "http://localhost:8000/api/data/upload" \
  -F "file=@文件路径"
```

**Windows 示例——上传示例数据：**
```bash
curl -X POST "http://localhost:8000/api/data/upload" ^
  -F "file=@C:\Users\qiufengm\Desktop\智慧水利应用\water_quality_system\data\samples\water_quality_sample.csv"
```

**注意：** Windows 系统请将 `\` 改为 `^` 换行，或直接写在一行：
```bash
curl -X POST "http://localhost:8000/api/data/upload" -F "file=@C:\Users\qiufengm\Desktop\智慧水利应用\water_quality_system\data\samples\water_quality_sample.csv"
```

**CSV 文件格式要求：**

| 列名 | 说明 | 示例 | 必填 |
|------|------|------|------|
| station_id | 站点编号 | ST001 | 是 |
| collection_time | 采集时间 | 2026-06-01 08:00:00 | 是 |
| ph | pH 值 | 7.2 | 否 |
| do | 溶解氧 (mg/L) | 6.5 | 否 |
| nh3n | 氨氮 (mg/L) | 0.15 | 否 |
| turbidity | 浊度 (NTU) | 3.2 | 否 |
| temperature | 水温 (℃) | 22.5 | 否 |
| cod | 化学需氧量 (mg/L) | 10.0 | 否 |
| total_phosphorus | 总磷 (mg/L) | 0.05 | 否 |

支持中文列名自动映射（例如"采集时间" → `collection_time`）。

**成功返回示例：**
```json
{
  "filename": "water_quality_sample.csv",
  "records_loaded": 540,
  "columns_detected": ["station_id", "collection_time", "ph", "do", ...],
  "preview": [...]
}
```

### 3.2 方式二：模拟传感器数据

无需外部文件，系统自动按时间序列生成带随机波动的模拟传感器数据。

```bash
curl -X POST "http://localhost:8000/api/data/upload/simulate" \
  -H "Content-Type: application/json" \
  -d "{\"station_id\": \"ST001\", \"hours\": 72}"
```

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| station_id | string | ST001 | 站点编号 |
| hours | int | 24 | 模拟小时数，每小时生成1条记录 |

**示例——生成 ST002 站点 48 小时数据：**
```bash
curl -X POST "http://localhost:8000/api/data/upload/simulate" \
  -H "Content-Type: application/json" \
  -d "{\"station_id\": \"ST002\", \"hours\": 48}"
```

### 3.3 方式三：手动录入

录入单条水质检测记录。

```bash
curl -X POST "http://localhost:8000/api/data/manual" \
  -H "Content-Type: application/json" \
  -d "{\"station_id\": \"ST001\", \"collection_time\": \"2026-06-02 08:00:00\", \"ph\": 7.2, \"do\": 6.5, \"nh3n\": 0.15}"
```

**必填字段：** `station_id`, `collection_time`
**可选字段：** `ph`, `do`, `nh3n`, `turbidity`, `temperature`, `cod`, `total_phosphorus`

---

## 4. 数据查询与统计

### 4.1 查询原始数据

```bash
# 分页查询（默认第1页，每页20条）
curl "http://localhost:8000/api/data/raw?page=1&page_size=10"
```

**返回字段：**
- `records` — 数据记录列表
- `total` — 总记录数
- `page` — 当前页码
- `page_size` — 每页条数

### 4.2 数据统计摘要

```bash
curl "http://localhost:8000/api/data/summary"
```

返回各水质指标的最小值、最大值、均值、标准差、缺失数。

### 4.3 查看站点列表（数据中）

```bash
curl "http://localhost:8000/api/data/stations"
```

返回当前已加载数据中包含的所有站点 ID。

### 4.4 数据状态信息

```bash
curl "http://localhost:8000/api/data/info"
```

返回是否有原始数据、是否有清洗后数据等状态信息。

---

## 5. 数据清洗

### 5.1 执行清洗

```bash
curl -X POST "http://localhost:8000/api/data/clean" \
  -H "Content-Type: application/json" \
  -d "{\"handle_missing\": \"interpolate\", \"outlier_method\": \"iqr\"}"
```

**参数说明：**

| 参数 | 选项 | 说明 |
|------|------|------|
| handle_missing | `drop` / `mean` / `median` / `interpolate` | 缺失值处理方式 |
| outlier_method | `none` / `iqr` / `zscore` | 异常值检测方法 |

**清洗流程：** 去重 → 缺失值处理 → 异常值检测 → 归一化

### 5.2 查看清洗后数据

```bash
curl "http://localhost:8000/api/data/cleaned?page=1&page_size=10"
```

---

## 6. ML 预测模型

### 6.1 训练模型

**方式一——基于已加载的原始数据清洗后训练：**
```bash
curl -X POST "http://localhost:8000/api/predict/train/from-data"
```

**方式二——使用样本数据直接训练：**
```bash
curl -X POST "http://localhost:8000/api/predict/train"
```

训练会为 7 个水质指标分别构建 XGBoost 回归模型（pH、DO、NH3N、浊度、水温、COD、总磷），并输出每个指标的 R²、MAE、RMSE。

### 6.2 查看模型信息

```bash
curl "http://localhost:8000/api/predict/model-info"
```

返回模型状态、训练指标、特征数量等信息。

### 6.3 执行预测

```bash
curl -X POST "http://localhost:8000/api/predict/batch?station_id=ST001&days=7"
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| station_id | string | — | 要预测的站点 |
| days | int | 7 | 未来预测天数 |

### 6.4 模型训练历史

```bash
curl "http://localhost:8000/api/predict/history"
```

列出所有历史训练记录。

---

## 7. 告警管理

### 7.1 查看告警规则

系统内置 12 条基于 GB 3838-2002《地表水环境质量标准》III 类标准的默认规则：

```bash
curl "http://localhost:8000/api/alert/rules"
```

**默认规则列表：**

| 指标 | 运算符 | 阈值 | 严重级别 |
|------|--------|------|----------|
| pH | < | 6.0 | critical |
| pH | > | 9.0 | critical |
| 溶解氧 DO | < | 2.0 | critical |
| 溶解氧 DO | < | 5.0 | warning |
| 氨氮 NH3N | > | 1.0 | critical |
| 氨氮 NH3N | > | 0.5 | warning |
| 浊度 Turbidity | > | 10.0 | warning |
| 浊度 Turbidity | > | 5.0 | info |
| 水温 Temperature | > | 35.0 | warning |
| 水温 Temperature | < | 0.0 | warning |
| COD | > | 30.0 | critical |
| 总磷 Total Phosphorus | > | 0.2 | warning |

### 7.2 更新规则

```bash
curl -X PUT "http://localhost:8000/api/alert/rules" \
  -H "Content-Type: application/json" \
  -d "[{\"indicator\": \"ph\", \"operator\": \"<\", \"threshold\": 5.5, \"severity\": \"critical\"}]"
```

### 7.3 执行告警检查

检查当前已加载的数据是否触发告警规则：

```bash
curl -X POST "http://localhost:8000/api/alert/check"
```

### 7.4 查看告警历史

```bash
curl "http://localhost:8000/api/alert/history?page=1&page_size=20"
```

**支持按严重级别过滤：**
```bash
curl "http://localhost:8000/api/alert/history?severity=critical"
```

### 7.5 清空告警历史

```bash
curl -X DELETE "http://localhost:8000/api/alert/history"
```

---

## 8. 后台管理

> 后台管理接口需要登录获取 token。默认管理员账号：`admin` / `admin123`

### 8.1 登录

```bash
# 登录获取 token（Windows PowerShell）
$TOKEN=$(curl -s -X POST "http://localhost:8000/api/admin/login" -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}' | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# 或直接复制 token
curl -s -X POST "http://localhost:8000/api/admin/login" -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```
从返回结果中复制 `access_token` 值，后续请求在 Header 中携带。

### 8.2 查看当前用户

```bash
curl -H "Authorization: Bearer 你的token" "http://localhost:8000/api/admin/me"
```

### 8.3 站点管理（需要 admin 角色）

**查看站点列表：**
```bash
curl -H "Authorization: Bearer 你的token" "http://localhost:8000/api/admin/stations"
```

**创建站点：**
```bash
curl -X POST "http://localhost:8000/api/admin/stations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 你的token" \
  -d "{\"station_id\": \"ST004\", \"name\": \"新建监测站\", \"location\": \"某地\", \"description\": \"测试站点\", \"contact\": \"管理员\"}"
```

**更新站点：**
```bash
curl -X PUT "http://localhost:8000/api/admin/stations/ST001" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 你的token" \
  -d "{\"name\": \"更新后的名称\"}"
```

**删除站点：**
```bash
curl -X DELETE "http://localhost:8000/api/admin/stations/ST004" \
  -H "Authorization: Bearer 你的token"
```

---

## 9. 数据导出

### 9.1 CSV 导出

```bash
# 原始数据 CSV
curl -o raw_data.csv "http://localhost:8000/api/export/raw/csv"

# 统计摘要 CSV
curl -o summary.csv "http://localhost:8000/api/export/summary/csv"
```

### 9.2 Excel 导出

```bash
# 原始数据 Excel
curl -o raw_data.xlsx "http://localhost:8000/api/export/raw/excel"

# 完整统计报告 Excel（多 sheet）
curl -o report.xlsx "http://localhost:8000/api/export/report"
```

`/api/export/report` 返回包含 4 个 sheet 的 Excel 文件：
1. 原始数据
2. 清洗后数据
3. 统计摘要（均值、最值、标准差、缺失数）
4. 数据信息（总记录数、站点列表、时间范围）

---

## 10. Web 前端操作指南

### 10.1 首页看板

访问 http://localhost:5173 进入首页看板，展示：
- 统计卡片：总记录数、站点数、告警数
- 各站点最新水质数据
- 快速操作入口

### 10.2 数据管理页面

1. 点击左侧导航「数据管理」
2. **上传文件**：点击上传区域选择 CSV 文件，或拖拽文件到上传区
3. **生成模拟数据**：选择站点和小时数，点击生成
4. **查看数据**：下方表格展示已加载的原始数据，支持分页
5. **清洗数据**：选择清洗参数，点击清洗按钮

### 10.3 水质预测页面

1. 点击左侧导航「水质预测」
2. 确保已上传数据并训练模型（点击"训练模型"按钮）
3. 选择站点和预测天数（滑杆调节 1-30 天）
4. 点击「开始预测」，ECharts 折线图展示各指标预测趋势

### 10.4 告警管理页面

1. 点击左侧导航「告警管理」
2. **规则管理**：可编辑表格中修改规则阈值、严重级别、启用/禁用
3. **告警统计**：顶部卡片显示各级别告警数量
4. **执行检查**：点击「执行检查」按钮，对当前数据触发告警检测
5. **历史记录**：下方表格展示分页告警历史

### 10.5 登录页面

1. 点击顶部导航「登录」
2. 输入用户名 `admin` 和密码 `admin123`
3. 登录成功后自动跳转，顶部显示用户名

### 10.6 后台管理页面

需登录后访问，点击左侧导航「后台管理」：
- **站点管理**：新增/编辑/删除监测站点
- **用户管理**：查看用户列表和角色

---

## 11. 常见问题

### Q1: 上传 CSV 提示 "No file uploaded"

确保 `-F` 参数中 `file=` 后面的路径正确，且文件存在。
```bash
# 检查文件是否存在
dir C:\Users\qiufengm\Desktop\智慧水利应用\water_quality_system\data\samples\water_quality_sample.csv
```

### Q2: 训练模型报错 "No data loaded"

先上传数据再训练：
```bash
# 1. 上传数据
curl -X POST "http://localhost:8000/api/data/upload" -F "file=@..."

# 2. 训练
curl -X POST "http://localhost:8000/api/predict/train/from-data"
```

### Q3: 前端页面空白或无法加载

1. 确认后端在 http://localhost:8000 运行
2. 确认前端在 http://localhost:5173 运行
3. 前端已配置代理，API 请求会自动转发到后端

### Q4: 登录返回 401

检查用户名密码是否正确：
```bash
curl -X POST "http://localhost:8000/api/admin/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"admin\", \"password\": \"admin123\"}"
```

### Q5: 如何运行测试

```bash
cd C:\Users\qiufengm\Desktop\智慧水利应用\water_quality_system
python -m pytest tests/ -v
```

### Q6: Swagger 文档在哪里

访问 http://localhost:8000/docs 查看交互式 API 文档。

---

> 文档版本 1.0 | 2026年6月 | 第2组 制作
