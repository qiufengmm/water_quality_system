# 第1周 AI 辅助编程计划

## 项目信息
- **项目名称**: 基于大数据与机器学习的水质监测与预测系统
- **开发周期**: 第1周（基础框架与数据层）— 2026/5/11 ~ 2026/5/17
- **AI工具**: Claude Code (Claude Opus 4.7 Sonnet 4.6)

## 本周开发目标
1. 搭建项目骨架（目录结构、配置管理、应用入口）
2. 实现多源数据采集模块（CSV导入、模拟传感器、手动录入）
3. 实现数据清洗与管理模块（清洗流水线、校验器、转换器）
4. 搭建FastAPI基础服务（健康检查、数据上传、数据清洗等API）
5. 创建示例数据集并编写单元测试

## 人员分工

| 成员 | 职责 | 配合方式 |
|------|------|----------|
| 数据工程 | 数据采集模块编码 | AI生成基础代码后手动调优 |
| 后端开发 | 数据清洗模块 + API开发 | AI生成核心逻辑，人工审核 |
| 前端开发 | 项目骨架 + 测试 | AI生成模板代码 |
| 文档统筹 | 文档 + 进度管理 | 使用AI生成文档框架 |

## AI辅助编程流程

### 阶段1: 需求理解与方案设计
```
用户需求 → AI分析设计文档 → AI提出架构方案 → 人工确认 → 生成Plan文件
```
- 输入：课程作业要求、概要设计报告、详细设计报告
- AI输出：项目架构方案、技术选型建议、周开发计划
- 人工确认：团队评审通过后进入编码阶段

### 阶段2: AI编码实施
```
AI Plan → 逐模块生成代码 → 人工Review → 测试验证 → 提交
```
每个模块的开发流程：
1. 向AI描述模块功能和接口规范
2. AI生成代码实现
3. 人工Review代码质量
4. 运行测试验证
5. 提交至GitHub

### 阶段3: 测试与验证
```
AI生成测试用例 → 运行测试 → 修复Bug → 回归测试
```

## AI编码指令历史记录

### 指令1: 项目骨架搭建
```
指令: 创建FastAPI项目骨架，包含config配置管理、Pydantic数据模型定义、
      main.py应用入口，遵循分层架构设计。
AI输出: src/config.py, src/models/schemas.py, src/main.py
状态: ✅ 已完成
```

### 指令2: 数据采集模块
```
指令: 实现多源数据采集模块，包括：
  1. BaseCollector抽象基类（定义collect/validate/save接口）
  2. CsvCollector（CSV/Excel文件导入，支持中文列名自动映射）
  3. SensorCollector（模拟传感器数据生成，支持异常注入）
  4. ManualCollector（手动录入接口，支持单条和批量）
AI输出: src/data_collection/*.py
状态: ✅ 已完成
```

### 指令3: 数据清洗模块
```
指令: 实现数据清洗模块，包括：
  1. DataCleaner清洗流水线（去重、缺失值处理、异常检测、归一化）
  2. WaterQualityValidator校验器（基于GB 3838-2002标准）
  3. DataTransformer转换器（时间格式统一、列名标准化）
AI输出: src/data_cleaning/*.py
状态: ✅ 已完成
```

### 指令4: API路由
```
指令: 实现FastAPI路由，包括：
  - GET /health 健康检查
  - POST /api/data/upload CSV上传
  - POST /api/data/upload/simulate 模拟数据生成
  - POST /api/data/manual 手动录入
  - GET /api/data/raw 原始数据查询
  - POST /api/data/clean 数据清洗
  - GET /api/data/cleaned 清洗数据查询
  - GET /api/data/summary 数据统计
AI输出: src/api/routes/*.py
状态: ✅ 已完成
```

### 指令5: 单元测试
```
指令: 编写数据采集和数据清洗模块的单元测试，覆盖正常流程和异常边界。
AI输出: tests/test_collection.py, tests/test_cleaning.py
状态: ✅ 已完成
```

### 指令6: 示例数据集
```
指令: 生成包含3个监测站点、30天、每4小时采集一次的模拟水质数据集，
      包含pH、DO、氨氮、浊度、水温、COD、总磷等指标。
AI输出: data/samples/generate_sample.py + water_quality_sample.csv
状态: ✅ 已完成
```

## Harness/Skills 工程计划

```json
// .claude/settings.json (skills configuration)
{
  "skills": {
    "water-quality-week1": {
      "description": "水质监测系统第1周开发 - 数据采集与清洗模块",
      "prompt": "实现水质监测系统的数据采集和数据清洗模块",
      "model": "sonnet"
    }
  }
}
```

## 本周完成内容清单

### 代码产出
| 文件 | 功能描述 | 代码行数 |
|------|----------|----------|
| src/config.py | 系统配置管理 | ~80行 |
| src/main.py | FastAPI应用入口 | ~40行 |
| src/models/schemas.py | Pydantic数据模型 | ~80行 |
| src/data_collection/base.py | 采集器基类 | ~80行 |
| src/data_collection/csv_collector.py | CSV文件导入 | ~80行 |
| src/data_collection/sensor_collector.py | 模拟传感器 | ~80行 |
| src/data_collection/manual_collector.py | 手动录入 | ~80行 |
| src/data_cleaning/cleaner.py | 清洗流水线 | ~150行 |
| src/data_cleaning/validators.py | 数据校验 | ~100行 |
| src/data_cleaning/transformers.py | 数据转换 | ~80行 |
| src/api/routes/health.py | 健康检查 | ~15行 |
| src/api/routes/data_routes.py | 数据管理API | ~150行 |
| tests/test_collection.py | 采集测试 | ~120行 |
| tests/test_cleaning.py | 清洗测试 | ~130行 |

### 文档产出
| 文件 | 说明 |
|------|------|
| README.md | 项目说明与进度表 |
| docs/architecture.md | 架构设计文档 |
| ai_plan/week1_plan.md | AI辅助编程计划 |

## 第2周开发预告
- ML模块：XGBoost水质预测模型开发
- 前端搭建：Vue 3 + Element Plus基础框架
- 可视化图表：水质趋势折线图、仪表盘
- 预测API接口

---

*计划生成时间: 2026-05-15 | AI辅助编程工具: Claude Code*
