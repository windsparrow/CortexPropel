# 示例和测试数据

本目录包含用于演示和测试CortexPropel功能的示例数据。

## 文件说明

- `demo_data.py` - 示例数据生成器脚本
- `sample_tasks.json` - 示例任务数据（运行demo_data.py后生成）
- `test_scenarios.json` - 测试场景数据（运行demo_data.py后生成）

## 使用方法

### 生成示例数据

```bash
python examples/demo_data.py
```

这将生成两个JSON文件：
- `sample_tasks.json` - 包含6个示例任务，涵盖不同的状态和优先级
- `test_scenarios.json` - 包含4个测试场景任务，用于测试特殊状态（逾期、即将到期等）

### 使用示例数据

生成示例数据后，你可以使用CLI命令来测试功能：

```bash
# 使用示例数据文件
python cortexpropel.py --tasks-file sample_tasks.json list

# 查看测试场景
python cortexpropel.py --tasks-file test_scenarios.json health

# 搜索任务
python cortexpropel.py --tasks-file sample_tasks.json search 设计
```

## 示例任务说明

### sample_tasks.json 中的任务

1. **完成项目需求分析** (高优先级，已完成)
   - 包含标签："已完成", "需求分析"
   
2. **设计数据库架构** (中优先级，进行中)
   - 截止日期：7天后
   
3. **实现用户认证模块** (高优先级，被阻塞)
   - 截止日期：10天后
   
4. **编写单元测试** (中优先级，待办)
   - 截止日期：14天后
   
5. **部署测试环境** (低优先级，待办)
   - 截止日期：5天后
   
6. **编写API文档** (中优先级，待办)
   - 截止日期：12天后

### test_scenarios.json 中的测试场景

1. **逾期的报告撰写** (高优先级，已逾期2天)
   
2. **即将到期的演示准备** (紧急优先级，明天到期)
   
3. **长时间运行的数据处理** (中优先级，进行中8天)
   
4. **被遗忘的任务** (低优先级，15天未更新)

这些示例数据可以帮助你测试CortexPropel的各种功能，包括任务管理、状态检查、搜索和健康报告等。