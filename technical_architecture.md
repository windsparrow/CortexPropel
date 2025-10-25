# CortexPropel 技术架构文档

## 1. 项目概述

CortexPropel 是一个基于 LangGraph 的智能任务管理代理产品，旨在通过自然语言交互帮助用户高效管理个人任务。第一阶段目标是实现一个能够管理个人任务的基础智能体，支持任务的录入、拆解、状态更新和基本规划功能。

## 2. 技术架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Interface                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                CortexPropel Agent                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Task Parser    │  │  Task Planner   │  │ Task Manager │ │
│  │     Node        │  │     Node        │  │    Node      │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  Data Access Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Task Model     │  │  JSON Storage   │  │ File Manager │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件

#### 2.2.1 LangGraph 智能体
- **任务解析节点 (Task Parser Node)**: 负责解析用户输入的自然语言，识别任务意图和关键信息
- **任务规划节点 (Task Planner Node)**: 负责将复杂任务拆解为可执行的子任务
- **任务管理节点 (Task Manager Node)**: 负责任务的创建、更新、查询和状态管理

#### 2.2.2 数据访问层
- **任务模型 (Task Model)**: 定义任务的数据结构和属性
- **JSON 存储 (JSON Storage)**: 负责任务数据的持久化存储
- **文件管理器 (File Manager)**: 负责文件操作和备份

#### 2.2.3 CLI 交互界面
- 提供命令行界面，支持自然语言输入
- 支持任务查询、状态更新等交互操作

## 3. 数据模型设计

### 3.1 任务模型 (Task Model)

```json
{
  "id": "string",                    // 唯一标识符
  "title": "string",                 // 任务标题
  "description": "string",           // 任务描述
  "status": "string",                // 任务状态: pending, in_progress, completed, cancelled
  "priority": "string",              // 优先级: low, medium, high, critical
  "created_at": "datetime",          // 创建时间
  "updated_at": "datetime",          // 更新时间
  "due_date": "datetime",            // 截止日期
  "estimated_duration": "integer",   // 预估时长(分钟)
  "actual_duration": "integer",      // 实际时长(分钟)
  "parent_id": "string",             // 父任务ID
  "subtasks": ["string"],            // 子任务ID列表
  "tags": ["string"],                // 标签列表
  "dependencies": ["string"],        // 依赖任务ID列表
  "resources": ["string"],           // 所需资源
  "progress": "integer",             // 进度百分比(0-100)
  "notes": "string"                  // 备注
}
```

### 3.2 项目模型 (Project Model)

```json
{
  "id": "string",                    // 唯一标识符
  "name": "string",                  // 项目名称
  "description": "string",           // 项目描述
  "created_at": "datetime",          // 创建时间
  "updated_at": "datetime",          // 更新时间
  "tasks": ["string"],               // 任务ID列表
  "settings": {                      // 项目设置
    "default_priority": "string",    // 默认优先级
    "working_hours": {               // 工作时间设置
      "start_time": "string",        // 开始时间 "HH:MM"
      "end_time": "string",          // 结束时间 "HH:MM"
      "weekdays": ["integer"]        // 工作日 [1-5] 表示周一到周五
    },
    "task_defaults": {               // 任务默认设置
      "estimated_duration": "integer" // 默认预估时长(分钟)
    }
  }
}
```

### 3.3 数据存储结构

```
cortex_propel_data/
├── projects/
│   ├── personal.json
│   └── work.json
├── tasks/
│   ├── personal/
│   │   ├── task_001.json
│   │   └── task_002.json
│   └── work/
│       ├── task_003.json
│       └── task_004.json
├── backups/
│   ├── 2023-12-01/
│   └── 2023-12-02/
└── config/
    └── settings.json
```

## 4. LangGraph 工作流设计

### 4.1 工作流状态

```
State = {
  "user_input": "string",           // 用户输入
  "intent": "string",               // 识别的意图
  "parsed_task": "object",          // 解析后的任务信息
  "action_plan": "array",           // 行动计划
  "result": "object",               // 执行结果
  "messages": "array"               // 对话历史
}
```

### 4.2 工作流节点

1. **输入解析节点 (Input Parser Node)**
   - 解析用户输入，识别意图
   - 提取任务关键信息
   - 确定下一步操作

2. **任务创建节点 (Task Creation Node)**
   - 根据解析结果创建新任务
   - 分配任务ID和初始属性
   - 保存到数据存储

3. **任务拆解节点 (Task Decomposition Node)**
   - 分析复杂任务
   - 拆解为子任务
   - 建立任务依赖关系

4. **任务更新节点 (Task Update Node)**
   - 更新任务状态和属性
   - 处理进度变更
   - 记录更新历史

5. **任务查询节点 (Task Query Node)**
   - 根据条件查询任务
   - 格式化查询结果
   - 返回任务信息

6. **响应生成节点 (Response Generation Node)**
   - 生成用户友好的响应
   - 提供操作反馈
   - 建议后续操作

### 4.3 工作流路由逻辑

```
def route_decision(state):
    intent = state["intent"]
    
    if intent == "create_task":
        return "task_creation_node"
    elif intent == "update_task":
        return "task_update_node"
    elif intent == "query_task":
        return "task_query_node"
    elif intent == "decompose_task":
        return "task_decomposition_node"
    else:
        return "response_generation_node"
```

## 5. 技术实现细节

### 5.1 依赖项

- Python 3.9+
- LangGraph: 用于构建智能体工作流
- LangChain: 用于LLM交互和提示管理
- Pydantic: 用于数据模型验证
- Click: 用于CLI界面
- Rich: 用于美化CLI输出
- python-dateutil: 用于日期时间处理

### 5.2 目录结构

```
cortex_propel/
├── src/
│   ├── cortex_propel/
│   │   ├── __init__.py
│   │   ├── agent/
│   │   │   ├── __init__.py
│   │   │   ├── nodes.py            # LangGraph节点实现
│   │   │   ├── workflow.py         # 工作流定义
│   │   │   └── state.py            # 状态定义
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── task.py             # 任务模型
│   │   │   └── project.py          # 项目模型
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   ├── json_storage.py     # JSON存储实现
│   │   │   └── file_manager.py     # 文件管理器
│   │   ├── cli/
│   │   │   ├── __init__.py
│   │   │   ├── commands.py         # CLI命令实现
│   │   │   └── ui.py               # UI组件
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── config.py           # 配置管理
│   │       ├── helpers.py          # 辅助函数
│   │       └── validators.py       # 验证器
├── tests/
│   ├── __init__.py
│   ├── test_agent/
│   ├── test_models/
│   ├── test_storage/
│   └── test_cli/
├── examples/
│   ├── basic_usage.py
│   └── advanced_features.py
├── docs/
│   ├── user_guide.md
│   └── api_reference.md
├── requirements.txt
├── setup.py
└── README.md
```

### 5.3 配置管理

```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "temperature": 0.1,
    "max_tokens": 1000
  },
  "storage": {
    "data_dir": "~/.cortex_propel",
    "backup_enabled": true,
    "backup_frequency": "daily"
  },
  "cli": {
    "default_project": "personal",
    "output_format": "rich",
    "confirm_destructive_actions": true
  }
}
```

## 6. 扩展性设计

### 6.1 插件架构

为支持未来功能扩展，系统采用插件架构：

```python
class Plugin:
    def __init__(self, name, version):
        self.name = name
        self.version = version
    
    def register_nodes(self, workflow):
        """注册自定义节点到工作流"""
        pass
    
    def register_commands(self, cli):
        """注册自定义CLI命令"""
        pass
```

### 6.2 数据存储扩展

当前使用JSON文件存储，未来可扩展为：

- 数据库存储 (SQLite, PostgreSQL)
- 云存储集成
- 多用户支持

### 6.3 可视化扩展

为支持甘特图等可视化功能，预留接口：

```python
class VisualizationProvider:
    def generate_gantt_chart(self, tasks):
        """生成甘特图"""
        pass
    
    def generate_dependency_graph(self, tasks):
        """生成依赖关系图"""
        pass
```

## 7. 安全性考虑

- 本地数据存储，确保隐私
- 敏感信息加密存储
- 定期数据备份
- 输入验证和清理

## 8. 性能优化

- 任务数据懒加载
- 查询结果缓存
- 批量操作支持
- 异步I/O操作

## 9. 测试策略

- 单元测试覆盖所有核心功能
- 集成测试验证工作流
- 性能测试确保响应速度
- 用户接受测试验证易用性

## 10. 部署和分发

- PyPI包分发
- Docker容器化支持
- 跨平台兼容性
- 自动更新机制

---

此文档将作为 CortexPropel 项目第一阶段开发的技术指导，确保系统的可扩展性和长期维护性。