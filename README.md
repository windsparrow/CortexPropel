# CortexPropel - 智能任务管理工具

CortexPropel 是一个基于 LangGraph 框架的智能任务管理工具，支持自然语言交互、任务自动建模和智能排期功能。

## 第1阶段功能

当前版本实现了以下核心功能：

1. **任务管理数据模型** - 定义了完整的任务数据结构，包括优先级、进度跟踪、时间戳等
2. **任务录入与更新** - 支持通过自然语言创建和更新任务
3. **任务执行检查** - 自动检查任务状态、进度和逾期情况
4. **任务排期** - 根据优先级和截止日期智能排期
5. **图表展现** - 支持多种图表可视化任务进度和状态

## 安装

```bash
pip install -e .
```

## 使用方法

### 添加任务
```bash
cortex add "完成项目文档编写，优先级高，截止日期2025-07-05"
```

### 列出所有任务
```bash
cortex list
```

### 检查任务执行状态
```bash
cortex check
```

### 查看推荐的任务排期
```bash
cortex schedule
```

### 生成任务报告
```bash
cortex report
```

### 更新任务进度
```bash
cortex progress <task_id> <progress_percentage>
```

### 更新任务状态
```bash
cortex status <task_id> <new_status>
```

### 生成文本可视化
```bash
cortex visualize
```

### 生成图表
```bash
# 生成所有图表
cortex chart all

# 生成特定类型的图表
cortex chart progress    # 进度条形图
cortex chart status      # 状态分布饼图
cortex chart priority    # 优先级分布图
cortex chart timeline    # 时间线图表
```

## 任务状态

- `todo` - 待办
- `in_progress` - 进行中
- `done` - 已完成

## 优先级

- `low` - 低
- `medium` - 中
- `high` - 高

## 数据存储

任务数据以 JSON 格式存储在 `tasks.json` 文件中，支持任务的创建、更新、查询和删除操作。

## 技术架构

- **框架**: LangGraph
- **存储**: JSON 文件
- **交互**: CLI 命令行界面
- **可视化**: Matplotlib 图表库

## 注意事项

1. 使用自然语言添加任务需要配置 DeepSeek API 密钥
2. 图表生成需要安装 Matplotlib 依赖
3. 任务数据存储在本地 JSON 文件中，请定期备份

## 后续计划

第2阶段将实现以下功能：
- 多用户支持
- 任务依赖关系
- 更丰富的可视化选项
- Web 界面