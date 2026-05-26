# 第2周 AI 辅助编程计划

## 项目信息
- **项目名称**: 基于大数据与机器学习的水质监测与预测系统
- **开发周期**: 第2周（核心智能与展示层）— 2026/5/18 ~ 2026/5/26
- **AI工具**: Claude Code (Claude Opus 4.7 + Sonnet 4.6)

## 本周开发目标
1. 修复特征工程滚动窗口Bug + 训练XGBoost水质预测模型
2. 实现预测API接口（训练/预测/模型信息/历史查询）
3. 搭建Vue 3 + Element Plus前端框架
4. 实现可视化看板（Dashboard/数据管理/预测分析页面）
5. 全流程集成测试与文档生成

## 人员分工

| 成员 | 职责 | 配合方式 |
|------|------|----------|
| 谢坤 | ML模型开发 + 预测API + 后端集成 | AI生成核心逻辑，人工审核训练效果 |
| 苏航 | Vue 3前端 + ECharts图表 | AI生成模板代码，手动调优样式 |
| 赵宏斌 | AI Plan文档 + Word报告 | AI生成文档框架 |
| 姜宇琦 | 集成测试 | 测试用例执行与验证 |

## AI辅助编程流程

### 阶段1: 需求理解与方案设计
```
用户需求 → AI分析第1周代码结构 → 设计ML架构 → 人工确认 → 生成Week 2 Plan
```
- 输入：第1周代码、需求分析报告、Week 1计划
- AI输出：ML模型架构、特征工程方案、前端页面设计
- 人工确认：团队评审通过

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
AI生成测试 → 运行测试 → 修复Bug → 回归测试
```

## AI编码指令历史记录

### 指令1: ML基础框架
```
指令: 创建水质预测ML模块，包括：
  1. AbstractPredictor抽象基类 + PredictionResult数据类
  2. FeatureEngineer特征工程（滞后特征、滚动统计、时间特征、One-Hot编码）
  3. XGBoostPredictor（训练/预测/保存/加载/特征重要性）
  4. 训练脚本（加载→清洗→特征→训练→评估→保存）
AI输出: src/ml/base.py, feature_engineer.py, xgboost_predictor.py, train.py
状态: ✅ 已完成
修复记录: 滚动窗口Bug（transform返回SeriesGroupBy需在内部聚合）、
          预测时特征列对齐（One-Hot编码列数不一致）
```

### 指令2: 预测API
```
指令: 实现预测API路由，包括：
  - POST /api/predict/train 基于样本数据训练
  - POST /api/predict/train/from-data 基于已加载数据训练
  - POST /api/predict/batch 批量预测
  - GET /api/predict/model-info 模型信息查询
  - GET /api/predict/history 历史模型列表
AI输出: src/api/routes/predict_routes.py
状态: ✅ 已完成
修复记录: 训练前增加数据清洗步骤（处理NaN值）
```

### 指令3: Vue 3前端项目
```
指令: 创建Vue 3 + Vite前端项目，包含：
  1. Vite + Vue 3项目初始化
  2. Element Plus + ECharts依赖安装
  3. Axios HTTP封装
  4. Vue Router（首页看板/数据管理/预测分析）
  5. 布局组件（侧边栏导航、头部标题）
AI输出: web/ 项目目录（package.json, vite.config.js, main.js, App.vue, router, api）
状态: ✅ 已完成
```

### 指令4: 前端页面开发
```
指令: 实现3个核心页面：
  1. Dashboard.vue — 首页看板（统计卡片、站点数据、快速操作入口）
  2. DataManagement.vue — 数据管理（CSV上传、数据清洗、数据表格浏览）
  3. Prediction.vue — 水质预测（站点选择、天数选择、模型训练、预测结果图表）
AI输出: web/src/views/Dashboard.vue, DataManagement.vue, Prediction.vue
状态: ✅ 已完成
```

### 指令5: Bug修复 - 特征工程滚动窗口
```
指令: 修复FeatureEngineer.create_features()中滚动统计的Bug
问题: transform(lambda x: x.rolling(...)) 返回SeriesGroupBy，
      调用mean()时报TypeError: cannot convert the series to <class 'float'>
修复: 直接在transform内部完成聚合，改为两行独立的transform调用
文件: src/ml/feature_engineer.py:66-71
状态: ✅ 已解决
```

### 指令6: Bug修复 - 预测时特征列对齐
```
指令: 修复XGBoost模型预测时特征列数不匹配的问题
问题: 训练时3个站点生成3个One-Hot列（77列特征），
      预测时单站点只生成1个One-Hot列（75列特征），
      XGBoost报错：Feature shape mismatch, expected: 77, got 75
修复: 
  1. feature_names首次拟合后锁定（_is_fitted标志）
  2. 预测时自动补全缺失列（赋值为0）
  3. 模型加载时设置_is_fitted=True
文件: src/ml/feature_engineer.py:94-97, xgboost_predictor.py:186-190,277,286
状态: ✅ 已解决
```

## Harness/Skills 工程计划

```json
{
  "skills": {
    "water-quality-week2": {
      "description": "水质监测系统第2周开发 - ML模型与前端可视化",
      "prompt": "实现水质预测ML模块和Vue 3前端可视化页面",
      "model": "sonnet"
    }
  }
}
```

## 本周完成内容清单

### 代码产出
| 文件 | 功能描述 | 代码行数 |
|------|----------|----------|
| src/ml/base.py | 预测器抽象基类 + PredictionResult | ~80行 |
| src/ml/feature_engineer.py | 特征工程（滞后/滚动/时间/One-Hot） | ~130行 |
| src/ml/xgboost_predictor.py | XGBoost预测器（训练/预测/保存/加载） | ~320行 |
| src/ml/train.py | 训练脚本（加载→清洗→训练→评估→保存） | ~130行 |
| src/api/routes/predict_routes.py | 预测API（5个端点） | ~180行 |
| web/vite.config.js | Vite构建配置（代理到FastAPI后端） | ~15行 |
| web/src/main.js | Vue应用入口（Element Plus/Router） | ~20行 |
| web/src/App.vue | 根布局（侧边栏+顶部导航） | ~70行 |
| web/src/router/index.js | 路由配置（3个页面） | ~30行 |
| web/src/api/index.js | Axios HTTP封装（15个接口） | ~70行 |
| web/src/views/Dashboard.vue | 首页看板（统计+站点+快速操作） | ~200行 |
| web/src/views/DataManagement.vue | 数据管理（上传+清洗+表格） | ~200行 |
| web/src/views/Prediction.vue | 预测分析（控制+ECharts图表+表格） | ~200行 |

**ML模块合计**: ~840行 Python
**前端模块合计**: ~800行 Vue/JS
**本周新增总计**: ~1640行

### 文档产出
| 文件 | 说明 |
|------|------|
| ai_plan/week2_plan.md | AI辅助编程记录（本周） |
| docs/generate_week2_report.py | Week 2 Word报告生成脚本 |
| 第2组-水质监测预测系统-第2周进度报告.docx | 第2周进度报告 |
| README.md | 更新项目进度和模块说明 |

### Bug修复
| Bug | 文件 | 原因 | 修复方案 |
|-----|------|------|----------|
| 滚动窗口TypeError | feature_engineer.py:66-71 | transform返回SeriesGroupBy | 内部聚合替换链式调用 |
| 特征列数不匹配 | feature_engineer.py:94-97 | create_features覆盖feature_names | _is_fitted锁定 + 预测列对齐 |
| 训练数据含NaN | predict_routes.py:85-93 | 原始数据未清洗直接训练 | 增加DataCleaner前置清洗 |

## 第3周开发预告
- 异常告警模块（阈值配置、自动触发、历史记录）
- 数据导出模块（Excel/PDF报表生成）
- 后台管理模块（JWT认证、RBAC权限、站点管理）
- 系统集成联调

---

*计划生成时间: 2026-05-26 | AI辅助编程工具: Claude Code*
