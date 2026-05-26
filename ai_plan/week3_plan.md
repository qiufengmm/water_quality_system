# 第3周 AI 辅助编程计划

## 项目信息
- **项目名称**: 基于大数据与机器学习的水质监测与预测系统
- **开发周期**: 第3周（功能完善与集成）— 2026/5/27 ~ 2026/6/2
- **AI工具**: Claude Code (Claude Opus 4.7 + Sonnet 4.6)

## 本周开发目标
1. 异常告警模块（阈值配置、自动触发、历史记录）
2. 数据导出增强（Excel报表生成）
3. 后台管理模块（JWT认证、RBAC权限、站点管理）
4. 前端告警管理页面 + 后台管理页面
5. 全流程集成测试与文档生成

## 人员分工

| 成员 | 职责 | 配合方式 |
|------|------|----------|
| 谢坤 | 告警引擎开发 + 后台管理API + 系统集成 | AI生成核心逻辑，人工审核安全策略 |
| 苏航 | Vue 3前端页面（告警管理/登录/后台管理） | AI生成模板代码，手动调优样式 |
| 赵宏斌 | AI Plan文档 + Word报告 | AI生成文档框架 |
| 姜宇琦 | 集成测试 + 数据导出测试 | 测试用例执行与验证 |

## AI辅助编程流程

### 阶段1: 需求理解与方案设计
```
用户需求 → AI分析第2周代码结构 → 设计模块架构 → 人工确认 → 生成Week 3 Plan
```
- 输入：第2周代码、系统现有API结构、前端路由配置
- AI输出：告警引擎设计、JWT认证方案、站点CRUD设计
- 人工确认：团队评审通过

### 阶段2: AI编码实施
```
AI Plan → 逐模块生成代码 → 人工Review → 测试验证 → 提交
```

### 阶段3: 测试与验证
```
AI生成测试 → 运行测试 → 修复Bug → 回归测试
```

## AI编码指令历史记录

### 指令1: 告警引擎
```
指令: 创建告警引擎模块，包括：
  1. AlertRule数据类（indicator/operator/threshold/severity/enabled）
  2. AlertRecord数据类（station_id/indicator/value/rule/severity/timestamp/status）
  3. AlertEngine（默认GB 3838-2002标准12条规则、check_dataframe、check_and_save、get_history）
  4. CSV文件持久化告警历史
AI输出: src/alerting/alert_engine.py, src/alerting/__init__.py
状态: ✅ 已完成
```

### 指令2: 告警API
```
指令: 实现告警API路由，包括：
  - GET /api/alert/rules 获取规则列表
  - PUT /api/alert/rules 更新阈值规则
  - POST /api/alert/check 对当前数据执行告警检查
  - GET /api/alert/history 告警历史分页查询
  - DELETE /api/alert/history 清空告警历史
AI输出: src/api/routes/alert_routes.py
状态: ✅ 已完成
```

### 指令3: 后台管理 - JWT认证
```
指令: 实现JWT认证和用户管理模块：
  1. User数据类 + UserManager（JSON文件持久化）
  2. create_access_token / verify_token
  3. get_current_user FastAPI依赖注入
  4. require_role权限检查工厂函数
  5. 默认管理员账号 admin/admin123
AI输出: src/admin/auth.py
状态: ✅ 已完成
```

### 指令4: 后台管理 - 站点管理 + API路由
```
指令: 实现站点管理模块和管理API：
  1. Station数据类 + StationManager（JSON持久化，预置3站点）
  2. admin_routes.py：登录/注册/用户列表/当前用户/站点CRUD
  3. 基于role的权限控制（admin/editor/viewer）
AI输出: src/admin/station_manager.py, src/api/routes/admin_routes.py
状态: ✅ 已完成
```

### 指令5: 数据导出增强
```
指令: 增强导出模块，增加Excel格式支持：
  1. GET /api/export/raw/excel 原始数据.xlsx下载
  2. GET /api/export/cleaned/excel 清洗数据.xlsx下载
  3. GET /api/export/report 完整报告Excel（多sheet：原始数据/清洗数据/统计摘要/数据信息）
AI输出: 修改 src/api/routes/export_routes.py
状态: ✅ 已完成
```

### 指令6: Vue 3前端页面
```
指令: 实现3个新前端页面：
  1. AlertManagement.vue — 规则配置表格（可编辑阈值/运算符/级别/启用开关）、
     告警统计卡片（严重/警告/信息）、执行检查按钮、告警历史分页表格
  2. Login.vue — 登录表单（用户名+密码）、演示账号提示、token存储到localStorage
  3. AdminDashboard.vue — 站点管理CRUD（对话框表单）、用户管理（admin角色专属）
AI输出: web/src/views/AlertManagement.vue, Login.vue, AdminDashboard.vue
状态: ✅ 已完成
```

### 指令7: 前端集成
```
指令: 集成新页面到现有前端：
  1. api/index.js 新增15个API函数 + Axios请求拦截器（自动附加Bearer token）
  2. router/index.js 新增3个路由 + 路由守卫（/admin需要登录）
  3. App.vue 侧边栏新增告警管理/后台管理菜单、顶部登录状态显示、下拉菜单退出
AI输出: 修改 web/src/api/index.js, router/index.js, App.vue
状态: ✅ 已完成
```

## 本周完成内容清单

### 代码产出
| 文件 | 功能描述 | 代码行数 |
|------|----------|----------|
| src/alerting/alert_engine.py | 告警引擎（规则/检查/历史/持久化） | ~180行 |
| src/alerting/__init__.py | 告警模块导出 | ~5行 |
| src/api/routes/alert_routes.py | 告警API（5个端点） | ~90行 |
| src/admin/auth.py | JWT认证+用户管理+站点管理 | ~280行 |
| src/admin/__init__.py | 管理模块标识 | ~1行 |
| src/api/routes/admin_routes.py | 管理API（8个端点） | ~150行 |
| src/api/routes/export_routes.py | 新增Excel导出（3个端点） | ~80行修 |
| web/src/views/AlertManagement.vue | 告警管理页面 | ~280行 |
| web/src/views/Login.vue | 登录页面 | ~120行 |
| web/src/views/AdminDashboard.vue | 后台管理页面 | ~280行 |
| web/src/api/index.js | 新增API函数+拦截器 | ~50行修 |
| web/src/router/index.js | 新增3个路由+守卫 | ~20行修 |
| web/src/App.vue | 侧边栏+登录状态 | ~40行修 |

**后端新增**: ~700行 Python
**前端新增**: ~700行 Vue/JS
**修改**: ~190行
**本周总计**: ~1590行

### 文档产出
| 文件 | 说明 |
|------|------|
| ai_plan/week3_plan.md | AI辅助编程记录（本周） |
| docs/generate_week3_report.py | Week 3 Word报告生成脚本 |
| 第2组-水质监测预测系统-第3周进度报告.docx | 第3周进度报告 |
| README.md | 更新项目进度和模块说明 |

### API总计（41个端点）
| 模块 | 端点数 | 路由文件 |
|------|--------|----------|
| 系统 | 1 | health.py |
| 数据管理 | 11 | data_routes.py |
| 数据导出 | 8 | export_routes.py |
| 预测 | 5 | predict_routes.py |
| 告警 | 5 | alert_routes.py |
| 后台管理 | 8 | admin_routes.py |

## 第4周开发预告
- 单元测试全覆盖（ML模块、告警模块、管理模块）
- 系统集成测试与Bug修复
- 验收文档完善
- 演示PPT制作

---

*计划生成时间: 2026-06-02 | AI辅助编程工具: Claude Code*
