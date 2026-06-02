# 基于大数据与机器学习的水质监测与预测系统

> 《智慧水利应用》课程大作业项目
> 组号：第2组

## 项目简介

本项目基于 Python 机器学习集成方案，构建多源水质数据全流程处理、智能水质预测分析、可视化展示与异常告警、基础系统管理四大核心功能，解决传统水质监测时效性差、预测性不足、数据杂乱的问题。

**技术栈**: Python 3.9+ · FastAPI · Pandas · Scikit-learn · XGBoost · Vue 3 · Element Plus · ECharts

## 团队分工

| 成员 | 角色 | 职责 |
|------|------|------|
|  | **负责人** | ML模型开发、预测API、后端集成 |
|  | 组员 | 数据采集与预处理、集成测试 |
|  | 组员 | Vue 3前端开发、ECharts可视化图表 |
|  | 组员 | AI Plan文档、Word报告、PPT制作 |

## 项目进度表

### 总体进度规划

| 周次 | 日期 | 阶段 | 核心任务 | 负责人 |
|------|------|------|----------|--------|
| **第1周** ✅ | 5/11-5/17 | 基础框架与数据层 | 项目脚手架、数据采集模块、数据清洗模块、FastAPI基础服务 | 数据工程、后端开发 |
| **第2周** ✅ | 5/18-5/26 | 核心智能与展示层 | XGBoost模型训练、水质预测API、Vue 3前端 + ECharts可视化 | 后端开发、前端开发 |
| **第3周** ✅ | 5/27-6/2 | 功能完善与集成 | 异常告警、数据导出增强、后台管理（JWT+RBAC+站点管理） | 文档统筹、全员 |
| **第4周** ✅ | 6/3-6/9 | 测试与验收 | 单元测试(183个)、集成测试、Bug修复、验收文档、演示PPT | 全员 |

### 第1周开发进度 ✅

| 任务 | 状态 | 完成人 | 说明 |
|------|------|--------|------|
| 项目骨架搭建 | ✅ 完成 | 前端开发 | 目录结构、配置管理、Pydantic模型、FastAPI入口 |
| 数据采集模块-CSV导入 | ✅ 完成 | 数据工程 | 支持CSV/Excel，自动映射中文列名 |
| 数据采集模块-模拟传感器 | ✅ 完成 | 数据工程 | 模拟pH/DO/氨氮/浊度等数据，支持异常注入 |
| 数据采集模块-手动录入 | ✅ 完成 | 数据工程 | 单条和批量录入，格式校验 |
| 数据清洗模块-清洗流水线 | ✅ 完成 | 后端开发 | 去重、缺失值处理(插值/填充)、异常检测(IQR/Z-Score) |
| 数据清洗模块-数据校验 | ✅ 完成 | 后端开发 | 基于GB 3838-2002标准的水质指标校验 |
| 数据清洗模块-数据转换 | ✅ 完成 | 后端开发 | 时间格式统一、列名标准化、单位转换 |
| FastAPI基础服务 | ✅ 完成 | 后端开发 | 8个REST API端点，含数据上传/查询/清洗/统计 |
| 示例数据集 | ✅ 完成 | 数据工程 | 3站点30天540条数据，含缺失值和异常值 |
| 单元测试 | ✅ 完成 | 前端开发 | 采集模块和清洗模块，覆盖正常/异常/边界情况 |
| AI Plan文档 | ✅ 完成 | 文档统筹 | AI辅助编程记录和进度管理 |
| GitHub仓库搭建 | ✅ 完成 | 文档统筹 | 仓库初始化、README、.gitignore |

### 第2周开发进度 ✅

| 任务 | 状态 | 完成人 | 说明 |
|------|------|--------|------|
| XGBoost水质预测模型 | ✅ 完成 | 后端开发 | 7个指标独立模型，77维特征，平均R²=0.8245 |
| 特征工程模块 | ✅ 完成 | 后端开发 | 滞后特征/滚动统计/差分/时间特征/One-Hot编码 |
| 训练脚本 | ✅ 完成 | 后端开发 | 加载→清洗→特征→训练→评估→保存完整流程 |
| 预测API（5个端点） | ✅ 完成 | 后端开发 | train/batch/model-info/history等接口 |
| Vue 3前端框架搭建 | ✅ 完成 | 前端开发 | Vite + Element Plus + Vue Router + Axios |
| 首页看板页面 | ✅ 完成 | 前端开发 | 统计卡片、站点数据卡片、快速操作入口 |
| 数据管理页面 | ✅ 完成 | 前端开发 | CSV上传、数据清洗、数据表格分页浏览 |
| 水质预测页面 | ✅ 完成 | 前端开发 | ECharts折线图展示7指标预测趋势 |
| API数据清洗前置 | ✅ 完成 | 后端开发 | 训练前自动清洗NaN数据 |
| 集成测试 | ✅ 完成 | 数据工程 | 全流程上传→清洗→训练→预测验证通过 |
| 第2周进度报告 | ✅ 完成 | 文档统筹 | Word文档、AI Plan文档 |

### 第3周开发进度 ✅

| 任务 | 状态 | 完成人 | 说明 |
|------|------|--------|------|
| 异常告警模块 | ✅ 完成 | 后端开发 | AlertEngine + 12条GB 3838-2002规则 + CSV持久化 |
| 告警API（5个端点） | ✅ 完成 | 后端开发 | 规则配置/检查/历史/清空 |
| 数据导出增强 - Excel | ✅ 完成 | 数据工程 | openpyxl多sheet报告导出 |
| JWT认证与用户管理 | ✅ 完成 | 后端开发 | login/register/token，JSON文件持久化 |
| 站点管理CRUD | ✅ 完成 | 后端开发 | 预置3站点，admin角色专属管理 |
| 后台管理API（8个端点） | ✅ 完成 | 后端开发 | 登录/用户/站点完整链路 |
| 前端告警管理页面 | ✅ 完成 | 前端开发 | 规则编辑表格、统计卡片、历史分页 |
| 前端登录页面 | ✅ 完成 | 前端开发 | 表单验证、token存储、路由跳转 |
| 前端后台管理页面 | ✅ 完成 | 前端开发 | 站点CRUD对话框、用户管理表格 |
| 前端集成（路由/拦截器/侧边栏） | ✅ 完成 | 前端开发 | 路由守卫、401自动跳转、登录状态 |
| 集成测试 | ✅ 完成 | 数据工程 | 全模块导入测试、41个路由注册验证 |
| 第3周进度报告 | ✅ 完成 | 文档统筹 | Word文档、AI Plan文档 |

### 第4周开发进度 ✅

| 任务 | 状态 | 完成人 | 说明 |
|------|------|--------|------|
| 单元测试—告警引擎 | ✅ 完成 | 前端开发 | 33个测试，覆盖规则/检查/持久化/历史 |
| 单元测试—认证管理 | ✅ 完成 | 数据工程 | 25个测试，用户/站点/JWT/权限 |
| 单元测试—DataManager | ✅ 完成 | 数据工程 | 17个测试，原始/清洗/持久化/清空 |
| 单元测试—特征工程 | ✅ 完成 | 前端开发 | 18个测试，滞后/滚动/差分/时间/One-Hot |
| 单元测试—XGBoost预测 | ✅ 完成 | 后端开发 | 28个测试，训练/预测/保存/加载/信息 |
| API集成测试 | ✅ 完成 | 前端开发 | 31个测试，httpx AsyncClient全路由验证 |
| Bug修复（NaN序列化等7个） | ✅ 完成 | 后端开发 | _safe_json辅助函数、测试隔离、异步兼容 |
| 验收文档 | ✅ 完成 | 文档统筹 | docs/acceptance_report.md |
| 演示PPT大纲 | ✅ 完成 | 文档统筹 | docs/week4_demo_ppt.md |
| 第4周进度报告 | ✅ 完成 | 文档统筹 | Word文档、AI Plan文档 |

## 项目结构

```
water_quality_system/
├── README.md                        # 项目说明文档
├── requirements.txt                 # Python依赖
├── .gitignore                       # Git忽略规则
├── config.yaml                      # 环境配置(可选)
├── ai_plan/
│   ├── week1_plan.md               # 第1周AI辅助编程记录
│   ├── week2_plan.md               # 第2周AI辅助编程记录
│   └── week3_plan.md               # 第3周AI辅助编程记录
├── data/
│   ├── raw/                         # 原始数据(自动生成)
│   ├── cleaned/                     # 清洗后数据(自动生成)
│   ├── users.json                   # 用户账户数据(自动生成)
│   ├── stations.json                # 站点信息数据(自动生成)
│   └── samples/
│       ├── generate_sample.py       # 示例数据生成器
│       └── water_quality_sample.csv # 示例数据集(540条)
├── docs/
│   ├── architecture.md             # 架构设计文档
│   ├── generate_report.py          # 第1周Word报告生成脚本
│   ├── generate_week2_report.py    # 第2周Word报告生成脚本
│   └── generate_week3_report.py    # 第3周Word报告生成脚本
│   ├── generate_week4_report.py    # 第4周Word报告生成脚本
│   ├── acceptance_report.md        # 验收文档
│   └── week4_demo_ppt.md           # 答辩PPT大纲
├── models/                         # 训练好的XGBoost模型(自动生成)
├── web/                            # Vue 3前端项目
│   ├── package.json                # 前端依赖配置
│   ├── vite.config.js              # Vite构建配置(代理到后端)
│   └── src/
│       ├── main.js                 # Vue应用入口
│       ├── App.vue                 # 根布局(侧边栏+顶部导航+登录状态)
│       ├── api/
│       │   └── index.js            # Axios HTTP封装(30+个接口+token拦截器)
│       ├── router/
│       │   └── index.js            # 路由配置(6个页面+路由守卫)
│       └── views/
│           ├── Dashboard.vue       # 首页看板
│           ├── DataManagement.vue  # 数据管理
│           ├── Prediction.vue      # 水质预测
│           ├── AlertManagement.vue # 告警管理 (第3周)
│           ├── Login.vue           # 登录 (第3周)
│           └── AdminDashboard.vue  # 后台管理 (第3周)
├── src/
│   ├── main.py                     # FastAPI应用入口
│   ├── config.py                   # 系统配置
│   ├── models/
│   │   └── schemas.py              # Pydantic数据模型
│   ├── data_collection/            # 模块1: 多源数据采集
│   │   ├── base.py                 # 采集器基类
│   │   ├── csv_collector.py        # CSV/Excel导入
│   │   ├── sensor_collector.py     # 模拟传感器数据
│   │   └── manual_collector.py     # 手动录入
│   ├── data_cleaning/              # 模块2: 数据清洗
│   │   ├── cleaner.py              # 清洗流水线
│   │   ├── validators.py           # 数据校验器
│   │   └── transformers.py         # 数据转换器
│   ├── ml/                         # 模块3: ML预测 (第2周)
│   │   ├── base.py                 # 预测器抽象基类
│   │   ├── feature_engineer.py     # 特征工程
│   │   ├── xgboost_predictor.py    # XGBoost预测器
│   │   └── train.py                # 训练脚本
    │   ├── alerting/                   # 模块5: 告警 (第3周)
    │   │   ├── alert_engine.py         # 告警引擎（规则/检查/持久化）
    │   │   └── __init__.py
    │   ├── admin/                      # 模块7: 后台管理 (第3周)
    │   │   ├── auth.py                 # JWT认证+用户管理+站点管理
    │   │   └── __init__.py
│   └── api/
│       └── routes/
│           ├── health.py           # 健康检查
│           ├── data_routes.py      # 数据管理API
│           └── predict_routes.py   # 预测API (第2周)
├── tests/
│   ├── conftest.py                 # 共享夹具（15个fixture）
│   ├── test_collection.py          # 采集模块测试
│   ├── test_cleaning.py            # 清洗模块测试
│   ├── test_alert_engine.py        # 告警引擎测试 (33个)
│   ├── test_auth.py                # 认证管理测试 (25个)
│   ├── test_data_manager.py        # 数据管理测试 (17个)
│   ├── test_feature_engine.py      # 特征工程测试 (18个)
│   ├── test_xgboost_predictor.py   # XGBoost预测器测试 (28个)
│   └── test_api_integration.py     # API集成测试 (31个)
```

## 快速开始

### 环境要求

- Python 3.9+
- pip / conda
- Node.js 18+ (前端)

### 后端安装与运行

```bash
# 1. 克隆仓库
git clone <repo-url>
cd water_quality_system

# 2. 安装依赖
pip install -r requirements.txt

# 3. 生成示例数据(可选)
cd data/samples
python generate_sample.py
cd ../..

# 4. 启动服务
uvicorn src.main:app --reload --port 8000

# 5. 访问API
# http://localhost:8000        - API信息
# http://localhost:8000/docs   - Swagger API文档
# http://localhost:8000/health - 健康检查
```

### 前端启动 (第2周新增)

```bash
# 1. 进入前端目录
cd web

# 2. 安装依赖
npm install

# 3. 启动开发服务器 (默认端口5173，自动代理API到8000)
npm run dev

# 4. 访问前端
# http://localhost:5173

# 5. 生产构建
npm run build
```

### API使用示例

```bash
# 1. 上传CSV数据
curl -X POST http://localhost:8000/api/data/upload \
  -F "file=@data/samples/water_quality_sample.csv"

# 2. 生成模拟数据
curl -X POST http://localhost:8000/api/data/upload/simulate \
  -d "station_id=ST001&hours=24&interval=60"

# 3. 查看原始数据
curl http://localhost:8000/api/data/raw?page=1&page_size=10

# 4. 执行数据清洗
curl -X POST http://localhost:8000/api/data/clean \
  -H "Content-Type: application/json" \
  -d '{"handle_missing": "interpolate", "outlier_method": "iqr"}'

# 5. 查看数据统计
curl http://localhost:8000/api/data/summary

# 6. 训练预测模型 (第2周新增)
curl -X POST http://localhost:8000/api/predict/train/from-data

# 7. 批量预测 (第2周新增)
curl -X POST "http://localhost:8000/api/predict/batch?station_id=ST001&days=7"

# 8. 查看模型信息 (第2周新增)
curl http://localhost:8000/api/predict/model-info
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行指定测试文件
pytest tests/test_alert_engine.py -v

# 跳过慢速训练测试
pytest tests/ -v -m "not slow"

# 查看测试覆盖率（需安装 pytest-cov）
pytest tests/ --cov=src
```

## 函数定义说明

### 数据采集模块

| 类/函数 | 文件 | 功能说明 |
|---------|------|----------|
| `BaseCollector` | `base.py` | 采集器抽象基类，定义 collect/validate/save 接口 |
| `CollectResult` | `base.py` | 采集结果数据类，含 success/records/errors |
| `CsvCollector.collect()` | `csv_collector.py` | 导入CSV/Excel文件，自动映射中文列名 |
| `CsvCollector.collect_batch()` | `csv_collector.py` | 批量导入多个文件 |
| `SensorCollector.collect()` | `sensor_collector.py` | 生成模拟传感器时序数据，支持随机异常值 |
| `ManualCollector.collect()` | `manual_collector.py` | 录入单条手动检测数据 |
| `ManualCollector.collect_batch()` | `manual_collector.py` | 批量录入多条数据 |

### 数据清洗模块

| 类/函数 | 文件 | 功能说明 |
|---------|------|----------|
| `DataCleaner.clean()` | `cleaner.py` | 执行完整清洗流水线（去重→缺失处理→异常检测→归一化） |
| `DataCleaner._remove_duplicates()` | `cleaner.py` | 基于全列去重 |
| `DataCleaner._handle_missing()` | `cleaner.py` | 缺失值处理（删除/均值填充/中位数填充/线性插值） |
| `DataCleaner._remove_outliers()` | `cleaner.py` | 异常值检测（IQR方法/Z-Score方法） |
| `DataCleaner._normalize()` | `cleaner.py` | 数据归一化（Min-Max/Z-Score） |
| `WaterQualityValidator.validate_dataframe()` | `validators.py` | 基于GB 3838-2002标准校验水质指标范围 |
| `DataTransformer.standardize_datetime()` | `transformers.py` | 统一时间格式 |
| `DataTransformer.standardize_columns()` | `transformers.py` | 标准化列名为snake_case |

### ML预测模块 (第2周新增)

| 类/函数 | 文件 | 功能说明 |
|---------|------|----------|
| `AbstractPredictor` | `ml/base.py` | 预测器抽象基类，定义train/predict/save_model/load_model接口 |
| `PredictionResult` | `ml/base.py` | 预测结果数据类（success/station_id/predictions/dates/confidence） |
| `FeatureEngineer.create_features()` | `ml/feature_engineer.py` | 从时序数据创建77维特征矩阵（滞后/滚动/差分/时间/One-Hot） |
| `FeatureEngineer.create_prediction_features()` | `ml/feature_engineer.py` | 创建预测特征（不含目标列） |
| `XGBoostPredictor.train()` | `ml/xgboost_predictor.py` | 训练7个水质指标XGBoost回归模型，返回R²/MAE/RMSE |
| `XGBoostPredictor.predict()` | `ml/xgboost_predictor.py` | 递进式多步预测未来水质指标 |
| `XGBoostPredictor.save_model()` | `ml/xgboost_predictor.py` | 保存模型+元数据+特征配置到磁盘 |
| `XGBoostPredictor.load_model()` | `ml/xgboost_predictor.py` | 从磁盘加载已训练的模型 |
| `train_model()` | `ml/train.py` | 完整训练流程（加载→清洗→特征→训练→评估→保存） |

### 预测API (第2周新增)

| 函数 | 路径 | 功能说明 |
|------|------|----------|
| `train_prediction_model()` | POST /api/predict/train | 基于样本数据训练XGBoost模型 |
| `train_from_loaded_data()` | POST /api/predict/train/from-data | 基于已加载数据清洗后训练 |
| `predict_batch()` | POST /api/predict/batch | 指定站点+天数批量预测 |
| `get_model_info()` | GET /api/predict/model-info | 查询当前模型信息（指标/特征数/R²） |
| `get_prediction_history()` | GET /api/predict/history | 查看历史训练模型列表 |

### 前端Vue组件 (第2周新增)

| 组件 | 文件 | 功能说明 |
|------|------|----------|
| `App.vue` | `web/src/App.vue` | 根布局（侧边栏导航+顶部标题+内容区） |
| `Dashboard.vue` | `web/src/views/Dashboard.vue` | 首页看板（统计卡片+站点数据+快速操作） |
| `DataManagement.vue` | `web/src/views/DataManagement.vue` | 数据管理（CSV上传+数据清洗+表格浏览） |
| `Prediction.vue` | `web/src/views/Prediction.vue` | 水质预测（控制面板+ECharts图表+详情表） |
| `api/index.js` | `web/src/api/index.js` | Axios HTTP封装（15个API接口函数） |
| `router/index.js` | `web/src/router/index.js` | Vue Router路由配置（6个路由+路由守卫） |
| `AlertManagement.vue` | `web/src/views/AlertManagement.vue` | 告警管理（规则配置+统计卡片+检查+历史） |
| `Login.vue` | `web/src/views/Login.vue` | 登录页面（表单验证+token存储） |
| `AdminDashboard.vue` | `web/src/views/AdminDashboard.vue` | 后台管理（站点CRUD+用户管理） |

### 告警引擎 (第3周新增)

| 类/函数 | 文件 | 功能说明 |
|---------|------|----------|
| `AlertRule` | `alerting/alert_engine.py` | 告警规则数据类（indicator/operator/threshold/severity） |
| `AlertRecord` | `alerting/alert_engine.py` | 告警记录数据类（station_id/indicator/value/timestamp） |
| `AlertEngine.check_dataframe()` | `alerting/alert_engine.py` | 检查DataFrame中所有记录触发的告警 |
| `AlertEngine.check_and_save()` | `alerting/alert_engine.py` | 检查并持久化新告警记录到CSV |
| `AlertEngine.get_history()` | `alerting/alert_engine.py` | 分页查询告警历史（支持按级别过滤） |

### 后台管理模块 (第3周新增)

| 类/函数 | 文件 | 功能说明 |
|---------|------|----------|
| `User` | `admin/auth.py` | 用户数据类（username/role/display_name） |
| `UserManager.authenticate()` | `admin/auth.py` | 验证用户名密码 |
| `UserManager.create_user()` | `admin/auth.py` | 创建新用户（带密码哈希） |
| `Station` | `admin/auth.py` | 站点数据类（station_id/name/location/description） |
| `StationManager.add_station()` | `admin/auth.py` | 新增监测站点 |
| `StationManager.update_station()` | `admin/auth.py` | 更新站点信息 |
| `create_access_token()` | `admin/auth.py` | 创建JWT访问令牌 |
| `verify_token()` | `admin/auth.py` | 验证JWT令牌 |
| `get_current_user()` | `admin/auth.py` | FastAPI依赖注入（从token获取用户） |
| `require_role()` | `admin/auth.py` | 角色权限检查依赖工厂 |

### API接口

| 函数 | 路径 | 功能说明 |
|------|------|----------|
| `health_check()` | GET /health | 系统健康检查 |
| `upload_csv()` | POST /api/data/upload | 上传CSV/Excel文件 |
| `upload_simulated()` | POST /api/data/upload/simulate | 生成模拟传感器数据 |
| `add_manual_record()` | POST /api/data/manual | 手动录入水质数据 |
| `get_raw_data()` | GET /api/data/raw | 分页查询原始数据 |
| `clean_data()` | POST /api/data/clean | 执行数据清洗 |
| `get_cleaned_data()` | GET /api/data/cleaned | 分页查询清洗后数据 |
| `get_data_summary()` | GET /api/data/summary | 数据统计摘要（均值、最值、缺失统计） |
| `get_alert_rules()` | GET /api/alert/rules | 获取告警规则列表 |
| `update_alert_rules()` | PUT /api/alert/rules | 更新告警阈值配置 |
| `check_alerts()` | POST /api/alert/check | 执行告警检查 |
| `get_alert_history()` | GET /api/alert/history | 告警历史分页查询 |
| `clear_alert_history()` | DELETE /api/alert/history | 清空告警历史 |
| `export_raw_excel()` | GET /api/export/raw/excel | 原始数据Excel导出 |
| `export_cleaned_excel()` | GET /api/export/cleaned/excel | 清洗数据Excel导出 |
| `export_full_report()` | GET /api/export/report | 完整统计报告Excel |
| `login()` | POST /api/admin/login | 用户登录获取JWT token |
| `register_user()` | POST /api/admin/register | 注册新用户（admin专属） |
| `list_users()` | GET /api/admin/users | 用户列表（admin专属） |
| `get_current_user()` | GET /api/admin/me | 当前用户信息 |
| `list_stations()` | GET /api/admin/stations | 站点列表 |
| `create_station()` | POST /api/admin/stations | 新增站点（admin专属） |
| `update_station()` | PUT /api/admin/stations/{id} | 更新站点（admin专属） |
| `delete_station()` | DELETE /api/admin/stations/{id} | 删除站点（admin专属） |

## 模型训练结果

使用540条样本数据（3站点，30天，每4小时采集），清洗后保留525条有效记录，训练504条（80%训练集/20%验证集）。

| 水质指标 | R² | MAE | RMSE | 评价 |
|---------|-----|-----|------|------|
| pH | 0.8316 | 0.055 | 0.068 | ✅ 优秀 |
| 溶解氧(DO) | 0.7040 | 0.170 | 0.211 | ✅ 良好 |
| 氨氮(NH3N) | 0.5576 | 0.021 | 0.027 | ⚠ 一般 |
| 浊度(Turbidity) | 0.9377 | 0.125 | 0.169 | ✅ 优秀 |
| 水温(Temperature) | 0.9155 | 0.530 | 0.735 | ✅ 优秀 |
| 化学需氧量(COD) | 0.9362 | 0.254 | 0.353 | ✅ 优秀 |
| 总磷(Total_P) | 0.8890 | 0.004 | 0.006 | ✅ 优秀 |
| **平均** | **0.8245** | — | — | ✅ 良好 |

## Bug修复记录

| Bug | 原因 | 修复方案 |
|-----|------|----------|
| 滚动窗口TypeError | transform返回SeriesGroupBy | 在transform内部直接完成rolling聚合 |
| 特征列数不匹配 | 训练77列vs预测75列(One-Hot差异) | 锁定feature_names + 预测时补全缺失列 |
| 训练数据含NaN | 原始数据未清洗直接训练 | 增加DataCleaner前置清洗步骤 |
| Windows GBK编码 | R²符号无法在控制台打印 | 用R^2替代R²符号 |
| do是JS保留关键字 | Vue模板中使用do作为参数名 | 重命名为doVal |

## AI辅助编程说明

本项目全程采用AI辅助编程标准流程，使用Claude Code作为AI编码助手。

**AI Plan文件**:
- `ai_plan/week1_plan.md` — 第1周AI辅助编程记录
- `ai_plan/week2_plan.md` — 第2周AI辅助编程记录（ML模型+前端开发+文档）
- `ai_plan/week3_plan.md` — 第3周AI辅助编程记录（告警+后台管理+导出增强）
- `ai_plan/week4_plan.md` — 第4周AI辅助编程记录（测试+验收+文档）

**第2周AI编码指令**:
1. CMD-01: 创建ML基础框架（Base + FeatureEngineer + XGBoostPredictor + Train）
2. CMD-02: 实现预测API路由（训练/预测/模型信息/历史）
3. CMD-03: 创建Vue 3 + Vite前端项目
4. CMD-04: 实现3个前端页面（Dashboard/DataManagement/Prediction）
5. CMD-05: 修复滚动窗口Bug + 特征列对齐Bug + 训练NaN Bug
6. CMD-06: 生成AI Plan文档 + Word报告生成脚本

**第3周AI编码指令**:
1. CMD-07: 创建告警引擎（AlertEngine + GB 3838-2002默认规则）
2. CMD-08: 实现告警API路由（规则配置/检查/历史）
3. CMD-09: 实现JWT认证和用户管理（UserManager + Token）
4. CMD-10: 实现站点管理CRUD和管理API
5. CMD-11: 增强数据导出（Excel多sheet报告）
6. CMD-12: 创建3个前端页面（告警管理/登录/后台管理）
7. CMD-13: 前端集成（路由/拦截器/侧边栏/登录状态）

**第4周AI编码指令**:
1. CMD-14: 创建共享夹具（conftest.py，15个fixture）
2. CMD-15: 创建测试文件（告警引擎/认证管理/DataManager/特征工程/XGBoost预测/API集成）
3. CMD-16: 修复测试Bug（NaN序列化/pytest-asyncio兼容/测试隔离/响应字段匹配）
4. CMD-17: 生成文档（AI Plan/验收报告/演示PPT/Word报告/README更新）

**代码统计**: 第2周新增约2070行代码（18个文件）。第3周新增约1590行代码（14个文件）。第4周新增约1860行测试代码 + 820行文档（12个文件）。

**系统总计**: 43个REST API端点 | 6个前端页面 | 7个功能模块 | 183个测试用例 | ~5960行代码

## 许可证

本项目仅用于《智慧水利应用》课程教学目的。
