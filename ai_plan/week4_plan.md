# 第4周 AI 辅助编程计划

## 项目信息
- **项目名称**: 基于大数据与机器学习的水质监测与预测系统
- **开发周期**: 第4周（测试与验收）— 2026/6/3 ~ 2026/6/9
- **AI工具**: Claude Code (Claude Opus 4.7 + Sonnet 4.6)

## 本周开发目标
1. 单元测试全覆盖（ML模块、告警模块、管理模块、DataManager）
2. 系统集成测试（httpx TestClient全路由验证）
3. Bug修复（NaN序列化、测试框架兼容性问题）
4. 验收文档完善（功能验收清单、测试覆盖统计）
5. 演示PPT制作（12页答辩大纲）
6. 开发文档生成（Word报告、README更新）

## 人员分工

| 成员 | 职责 | 配合方式 |
|------|------|----------|
| 前端开发 | 单元测试编写（6个测试文件） | AI生成测试框架，人工确认边界条件 |
| 后端开发 | Bug修复 + 集成测试 | AI定位问题根因，人工选择修复方案 |
| 数据工程 | 端到端集成测试 | AI生成httpx TestClient测试 |
| 文档统筹 | AI Plan文档 + Word报告 + 验收文档 + PPT | AI生成文档框架，人工补充数据 |

## AI辅助编程流程

### 阶段1: 测试框架设计
```
现有代码结构 → AI分析各模块接口 → 设计测试策略 → 人工确认 → 生成conftest.py
```
- 输入：alert_engine.py、auth.py、data_manager.py、feature_engineer.py、xgboost_predictor.py API路由
- AI输出：共享夹具（15个fixture）、各模块测试类结构
- 人工确认：测试覆盖范围、边界条件

### 阶段2: AI测试编码
```
AI Plan → 逐模块生成测试 → 运行测试 → 修复Bug → 回归测试
```

### 阶段3: 文档生成
```
测试结果 → AI生成报告 → 人工补充数据 → 最终输出
```

## AI编码指令历史记录

### 指令1: 共享夹具 (conftest.py)
```
指令: 创建 tests/conftest.py，提供15个共享fixture:
  1. sample_df — 10行2站点标准水质DataFrame
  2. sample_df_with_alerts — 超阈值数据（触发告警）
  3. sample_training_df — 60行（30天×2站点），ML训练用
  4. temp_data_dir — 临时目录
  5. valid_token / viewer_token — 预生成JWT token
  6. auth_headers / viewer_headers — Authorization头
  7. client — httpx AsyncClient全栈测试
```

### 指令2: 告警引擎测试
```
指令: 创建 tests/test_alert_engine.py，33个测试，覆盖:
  - AlertRule/AlertRecord数据类（字段/默认值/操作符/严重级别）
  - AlertEngine初始化（12条默认规则/自定义规则）
  - check_dataframe（正常数据无告警/超阈值触发/禁用规则/空列/空DF）
  - check_and_save（CSV持久化/无告警不保存）
  - get_history（空历史/分页/严重级别过滤）
  - clear_history/update_rules
修复: 自定义规则dict转换、单例隔离（isolated_engine fixture）
```

### 指令3: 认证管理测试
```
指令: 创建 tests/test_auth.py，25个测试，覆盖:
  - UserManager初始化（默认admin/持久化）
  - UserManager认证（正确/错误密码/禁用用户/bcrypt格式）
  - UserManager CRUD（创建/重复/排除密码）
  - StationManager CRUD（新增/重复/更新/删除）
  - JWT函数（创建/验证/过期/无效token）
  - require_role（admin访问/viewer拒绝/未认证401）
修复: 持久化隔离（isolate_persistence fixture）、pytest-asyncio兼容性
```

### 指令4: DataManager测试
```
指令: 创建 tests/test_data_manager.py，17个测试，覆盖:
  - 初始化状态（has_raw/clear）
  - Raw数据（set/append/get_station_list）
  - Cleaned数据（set/get）
  - 清空操作（clear_raw/clear_cleaned/clear_all）
  - get_data_info（清洗前后信息对比）
```

### 指令5: 特征工程测试
```
指令: 创建 tests/test_feature_engine.py，18个测试，覆盖:
  - 初始化参数（lag_steps/rolling_window）
  - create_features（滞后/滚动/差分/时间/One-Hot特征）
  - NaN行丢弃
  - create_prediction_features（目标列移除）
  - 边界情况（单站点/缺失列/默认目标列）
```

### 指令6: XGBoost预测器测试
```
指令: 创建 tests/test_xgboost_predictor.py，28个测试，覆盖:
  - PredictionResult数据类
  - AbstractPredictor抽象基类
  - XGBoostPredictor初始化/训练/预测/保存/加载/信息查询
  - 使用n_estimators=20加速训练
```

### 指令7: API集成测试
```
指令: 创建 tests/test_api_integration.py，31个测试，httpx AsyncClient全栈测试:
  - 健康检查（GET /health, GET /）
  - 数据上传（CSV/模拟/手动）
  - 数据查询（原始/统计/站点/信息）
  - 数据清洗（有数据/无数据）
  - 告警流（规则/更新/检查/历史）
  - 认证流（登录/失败/me/未认证）
  - 站点管理（CRUD/权限）
  - 导出（CSV/Excel/报告）
  - 预测（模型信息/训练/历史）
修复: ASGITransport异步兼容、NaN序列化Bug（_safe_json辅助函数）
```

### 指令8: 文档生成
```
指令: 生成Word报告/验收文档/演示PPT大纲/README更新
  - docs/generate_week4_report.py: 11章节Word报告
  - docs/acceptance_report.md: 功能验收清单+测试覆盖+Bug清单
  - docs/week4_demo_ppt.md: 12页答辩PPT大纲
  - README.md: 更新第4周进度、测试统计
```

## Bug修复记录

| Bug | 原因 | 修复方案 |
|-----|------|----------|
| 自定义规则dict不转换 | __init__只转换DEFAULT_RULES | 统一使用AlertRule对象传入 |
| 告警历史读取真实文件 | AlertEngine单例共享CSV路径 | isolated_engine fixture隔离temp路径 |
| 测试数据跨用例污染 | UserManager/StationManager JSON持久化 | isolate_persistence fixture重定向到temp文件 |
| pytest-asyncio兼容性 | 0.25.3 STRICT模式不支持普通fixture | 使用@pytest_asyncio.fixture或@ pytest.mark.asyncio |
| NaN JSON序列化500 | std()返回NaN无法json.dumps | _safe_json辅助函数替换NaN为None |
| httpx ASGITransport同步 | v0.28.1不支持sync context manager | 全文件转为async/await |
| 测试expect与实际响应不匹配 | simulate返回records而非record_count | 修正test assertions匹配实际API响应 |

## 测试统计

| 测试文件 | 测试数 | 覆盖模块 |
|----------|--------|----------|
| test_alert_engine.py | 33 | 告警引擎（规则/检查/持久化） |
| test_auth.py | 25 | 认证管理（用户/站点/JWT/权限） |
| test_data_manager.py | 17 | 数据管理（原始/清洗/持久化） |
| test_feature_engine.py | 18 | 特征工程（创建/预测/边界） |
| test_xgboost_predictor.py | 28 | XGBoost预测器（训练/预测/保存） |
| test_api_integration.py | 31 | API全路由集成测试 |
| test_collection.py | 12 | 数据采集（Week 1遗留） |
| test_cleaning.py | 19 | 数据清洗（Week 1遗留） |
| **合计** | **183** | **全模块覆盖** |

## 代码统计

- 测试文件：8个（6个新增 + 2个Week 1遗留）
- 测试用例：183个（156个新增）
- 新增代码：约1860行
- 修复Bug：7个
- 文档产出：6个文件（AI Plan + Word报告 + 验收文档 + PPT大纲 + README更新 + conftest.py）
