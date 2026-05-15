# 基于大数据与机器学习的水质监测与预测系统

> 《智慧水利应用》课程大作业项目
> 组号：第2组

## 项目简介

本项目基于 Python 机器学习集成方案，构建多源水质数据全流程处理、智能水质预测分析、可视化展示与异常告警、基础系统管理四大核心功能，解决传统水质监测时效性差、预测性不足、数据杂乱的问题。

**技术栈**: Python 3.9+ · FastAPI · Pandas · Scikit-learn · XGBoost · Vue 3 · MySQL

## 团队分工

| 成员 | 角色 | 职责 |
|------|------|------|
| 谢坤 | **负责人** | 数据建模、模型开发与封装 |
| 姜宇琦 | 组员 | 数据采集与预处理 |
| 苏航 | 组员 | 可视化、前端 |
| 赵宏斌 | 组员 | 模块对接、PPT制作与展示 |

## 项目进度表

### 总体进度规划

| 周次 | 日期 | 阶段 | 核心任务 | 负责人 |
|------|------|------|----------|--------|
| **第1周** | 5/11-5/17 | 基础框架与数据层 | 项目脚手架、数据采集模块、数据清洗模块、FastAPI基础服务 | 姜宇琦、谢坤 |
| **第2周** | 5/18-5/24 | 核心智能与展示层 | ML模型训练与预测、Vue3可视化界面、预测API | 谢坤、苏航 |
| **第3周** | 5/25-5/31 | 功能完善与集成 | 异常告警、数据导出、后台管理、系统集成联调 | 赵宏斌、全员 |
| **第4周** | 6/1-6/7 | 测试与验收 | 单元测试、集成测试、Bug修复、验收准备 | 全员 |

### 第1周开发进度 (当前)

| 任务 | 状态 | 完成人 | 说明 |
|------|------|--------|------|
| 项目骨架搭建 | ✅ 完成 | 苏航 | 目录结构、配置管理、Pydantic模型、FastAPI入口 |
| 数据采集模块-CSV导入 | ✅ 完成 | 姜宇琦 | 支持CSV/Excel，自动映射中文列名 |
| 数据采集模块-模拟传感器 | ✅ 完成 | 姜宇琦 | 模拟pH/DO/氨氮/浊度等数据，支持异常注入 |
| 数据采集模块-手动录入 | ✅ 完成 | 姜宇琦 | 单条和批量录入，格式校验 |
| 数据清洗模块-清洗流水线 | ✅ 完成 | 谢坤 | 去重、缺失值处理(插值/填充)、异常检测(IQR/Z-Score) |
| 数据清洗模块-数据校验 | ✅ 完成 | 谢坤 | 基于GB 3838-2002标准的水质指标校验 |
| 数据清洗模块-数据转换 | ✅ 完成 | 谢坤 | 时间格式统一、列名标准化、单位转换 |
| FastAPI基础服务 | ✅ 完成 | 谢坤 | 8个REST API端点，含数据上传/查询/清洗/统计 |
| 示例数据集 | ✅ 完成 | 姜宇琦 | 3站点30天540条数据，含缺失值和异常值 |
| 单元测试 | ✅ 完成 | 苏航 | 采集模块和清洗模块，覆盖正常/异常/边界情况 |
| AI Plan文档 | ✅ 完成 | 赵宏斌 | AI辅助编程记录和进度管理 |
| GitHub仓库搭建 | 🔲 待办 | 赵宏斌 | 仓库初始化、README、.gitignore |

### 第2周规划

| 任务 | 负责人 | 预计产出 |
|------|--------|----------|
| XGBoost水质预测模型开发 | 谢坤 | 训练脚本、模型文件、预测函数 |
| 特征工程（相关性分析、特征筛选） | 谢坤 | 特征重要性分析报告 |
| Vue 3 + Element Plus前端框架搭建 | 苏航 | 前端项目骨架 |
| 水质趋势可视化（折线图、仪表盘） | 苏航 | Plotly/ECharts图表组件 |
| 预测API接口 /api/predict/batch | 谢坤+苏航 | 联调通过的预测服务 |
| 实时数据展示页面 | 苏航 | Web页面可查看实时数据 |

### 第3周规划

| 任务 | 负责人 | 预计产出 |
|------|--------|----------|
| 异常告警模块（阈值配置、自动触发） | 赵宏斌 | 告警引擎、告警历史 |
| 数据导出（Excel/PDF报表） | 姜宇琦 | 导出功能、统计报表 |
| 后台管理（JWT认证、RBAC、站点管理） | 谢坤 | 登录注册、权限控制、点位管理 |
| 系统集成联调 | 全员 | 全流程打通 |

### 第4周规划

| 任务 | 负责人 | 预计产出 |
|------|--------|----------|
| 单元测试全覆盖 | 苏航 | 各模块测试用例 |
| 集成测试 | 全员 | 端到端测试 |
| Bug修复 | 全员 | 问题单关闭 |
| 验收文档完善 | 赵宏斌 | 验收报告 |

## 项目结构

```
water_quality_system/
├── README.md                        # 项目说明文档
├── requirements.txt                 # Python依赖
├── .gitignore                       # Git忽略规则
├── config.yaml                      # 环境配置(可选)
├── ai_plan/
│   └── week1_plan.md               # 第1周AI辅助编程记录
├── data/
│   ├── raw/                         # 原始数据(自动生成)
│   ├── cleaned/                     # 清洗后数据(自动生成)
│   └── samples/
│       ├── generate_sample.py       # 示例数据生成器
│       └── water_quality_sample.csv # 示例数据集(540条)
├── docs/
│   └── architecture.md             # 架构设计文档
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
│   ├── ml/                         # 模块3: ML (第2周)
│   ├── visualization/              # 模块4: 可视化 (第2周)
│   ├── alerting/                   # 模块5: 告警 (第3周)
│   ├── export/                     # 模块6: 导出 (第3周)
│   ├── admin/                      # 模块7: 后台管理 (第3周)
│   └── api/
│       └── routes/
│           ├── health.py           # 健康检查
│           └── data_routes.py      # 数据管理API
└── tests/
    ├── test_collection.py          # 采集模块测试
    └── test_cleaning.py            # 清洗模块测试
```

## 快速开始

### 环境要求

- Python 3.9+
- pip / conda

### 安装与运行

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
```

### 运行测试

```bash
pytest tests/ -v
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

## AI辅助编程说明

本项目全程采用AI辅助编程标准流程，使用Claude Code作为AI编码助手。

**AI Plan文件**: `ai_plan/week1_plan.md` 包含：
- AI辅助编程流程定义
- 编码指令历史记录
- 各模块AI生成代码清单
- Harness/Skills配置说明

## 许可证

本项目仅用于《智慧水利应用》课程教学目的。
