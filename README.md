# CortexPropel

CortexPropel 是一个智能任务管理系统，集成了 DeepSeek AI 模型，提供任务分析、建议生成和顺序优化功能。

## 功能特性

- **任务管理**: 创建、更新、删除和列出任务
- **任务依赖**: 支持任务间的依赖关系管理
- **子任务**: 支持任务的层级结构
- **任务执行**: 提供任务执行器和调度器
- **AI 驱动**: 集成 DeepSeek API 进行智能任务分析
- **命令行界面**: 提供友好的 CLI 工具

## 安装

1. 克隆仓库:
```bash
git clone https://github.com/yourusername/CortexPropel.git
cd CortexPropel
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

3. 配置环境变量:
```bash
export DEEPSEEK_API_KEY="your_api_key_here"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
```

## 使用方法

### 命令行界面

#### 交互式聊天模式
```bash
python -m src.cli.main chat
```

#### 单次对话模式
```bash
python -m src.cli.main chat "创建一个新任务：完成项目文档"
```

#### 添加任务
```bash
python -m src.cli.main add "完成项目文档" --priority high --status pending
```

#### 列出任务
```bash
# 列出所有任务
python -m src.cli.main list

# 按状态过滤
python -m src.cli.main list --status pending

# 按优先级过滤
python -m src.cli.main list --priority high

# 按父任务过滤
python -m src.cli.main list --parent-id 1
```

#### AI 功能
```bash
# 分析任务
python -m src.cli.main analyze --task-ids 1,2,3

# 生成任务建议
python -m src.cli.main suggest --project-name "我的项目" --context "需要完成的任务"

# 优化任务顺序
python -m src.cli.main optimize --task-ids 1,2,3

# 检查 API 连接
python -m src.cli.main check-api
```

### Python API

```python
from src.services import TaskService, DeepSeekClient
from src.agents import TaskAgent

# 创建服务实例
task_service = TaskService()
deepseek_client = DeepSeekClient()
task_agent = TaskAgent(task_service, deepseek_client)

# 创建任务
task = task_service.create_task("完成项目文档", priority=Priority.HIGH)

# 分析任务
analysis = deepseek_client.analyze_task(task.to_dict())

# 生成任务建议
suggestions = deepseek_client.generate_task_suggestions("我的项目", "需要完成的任务")

# 优化任务顺序
optimized_order = deepseek_client.optimize_task_order([task1, task2, task3])
```

## 项目结构

```
CortexPropel/
├── src/
│   ├── agents/          # 任务智能体
│   ├── cli/             # 命令行界面
│   ├── models/          # 数据模型
│   └── services/        # 服务层
├── tests/               # 测试文件
│   ├── unit/            # 单元测试
│   └── integration/     # 集成测试
├── docs/                # 文档
├── requirements.txt     # 依赖列表
├── pytest.ini          # 测试配置
└── README.md           # 项目说明
```

## 开发

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行特定测试文件
pytest tests/unit/test_task_model.py

# 运行带详细输出的测试
pytest -v

# 运行带覆盖率报告的测试
pytest --cov=src tests/
```

### 代码风格

本项目使用 PEP 8 代码风格指南。建议使用以下工具:

```bash
# 安装代码格式化工具
pip install black flake8

# 格式化代码
black src/ tests/

# 检查代码风格
flake8 src/ tests/
```

## API 参考

### DeepSeek API

DeepSeek API 提供以下功能:

- `chat_completion`: 通用聊天完成
- `simple_chat`: 简化聊天接口
- `analyze_task`: 分析任务
- `generate_task_suggestions`: 生成任务建议
- `optimize_task_order`: 优化任务顺序
- `is_available`: 检查 API 可用性

### 任务服务

TaskService 提供以下方法:

- `create_task`: 创建任务
- `get_task`: 获取任务
- `update_task`: 更新任务
- `delete_task`: 删除任务
- `list_tasks`: 列出任务
- `add_subtask`: 添加子任务
- `add_dependency`: 添加依赖关系

## 贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目链接: [https://github.com/yourusername/CortexPropel](https://github.com/yourusername/CortexPropel)
- 问题反馈: [Issues](https://github.com/yourusername/CortexPropel/issues)

## 更新日志

### v0.1.0 (2023-XX-XX)

- 初始版本发布
- 基本任务管理功能
- DeepSeek API 集成
- 命令行界面
- 测试覆盖