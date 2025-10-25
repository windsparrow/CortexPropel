# CortexPropel LLM Provider Management

本项目已成功实现了多LLM提供商管理功能，支持OpenAI、Azure OpenAI、Anthropic、Cohere、Hugging Face和自定义OpenAI兼容的API端点。

## 已完成的功能

### 1. LLM提供商工厂类
- 实现了`LLMProviderFactory`类，支持创建不同提供商的LLM实例
- 支持获取所有支持的提供商列表
- 支持获取特定提供商的可用模型列表

### 2. 配置管理
- 实现了`LLMSettings`类，用于存储LLM配置
- 支持从配置文件、环境变量和CLI命令配置LLM
- 支持API密钥的安全存储和脱敏显示

### 3. CLI命令
- 实现了LLM相关的CLI命令：
  - `llm list` - 列出所有支持的提供商
  - `llm models <provider>` - 列出指定提供商的可用模型
  - `llm current` - 显示当前LLM配置
  - `llm configure <provider>` - 配置LLM提供商
  - `llm test <provider>` - 测试与提供商的连接

### 4. 示例和文档
- 创建了LLM提供商管理示例脚本
- 创建了详细的文档，说明如何使用和配置不同的LLM提供商

## 使用方法

### 使用CLI命令

```bash
# 列出所有支持的提供商
python -m src.cortex_propel.cli.main llm list

# 查看特定提供商的可用模型
python -m src.cortex_propel.cli.main llm models anthropic

# 查看当前配置
python -m src.cortex_propel.cli.main llm current

# 配置提供商
python -m src.cortex_propel.cli.main llm configure anthropic --model claude-3-haiku-20240307

# 测试连接
python -m src.cortex_propel.cli.main llm test anthropic
```

### 使用代码

```python
from cortex_propel.llm.llm_provider import LLMProviderFactory
from cortex_propel.config.settings import LLMSettings

# 创建设置
settings = LLMSettings(
    provider="anthropic",
    model="claude-3-haiku-20240307",
    api_key="your-api-key",
    temperature=0.7,
    max_tokens=1000
)

# 创建LLM实例
llm = LLMProviderFactory.create_llm(settings)

# 使用LLM
response = llm.invoke("Hello, how are you?")
print(response.content)
```

## 测试结果

所有功能已通过测试：

1. LLM提供商工厂类测试通过
2. CLI命令测试通过
3. 配置保存和加载测试通过
4. 示例脚本运行成功

## 支持的提供商

1. **OpenAI** - OpenAI的GPT模型（gpt-3.5-turbo, gpt-4, gpt-4-turbo）
2. **Azure OpenAI** - Azure OpenAI服务
3. **Anthropic** - Anthropic的Claude模型（claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307）
4. **Cohere** - Cohere的模型
5. **Hugging Face** - Hugging Face模型
6. **Custom** - 任何OpenAI兼容的API端点

## 环境变量

可以使用以下环境变量配置API密钥：

```bash
# OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# Azure OpenAI
export AZURE_OPENAI_API_KEY="your-azure-openai-api-key"
export AZURE_OPENAI_ENDPOINT="your-azure-openai-endpoint"
export AZURE_OPENAI_API_VERSION="2023-12-01-preview"

# Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Cohere
export COHERE_API_KEY="your-cohere-api-key"

# Hugging Face
export HUGGINGFACEHUB_API_TOKEN="your-huggingface-token"

# Custom OpenAI-compatible
export CUSTOM_OPENAI_API_KEY="your-custom-api-key"
export CUSTOM_OPENAI_ENDPOINT="your-custom-endpoint"
```

## 已解决的问题

1. **LangChain版本兼容性问题** - 升级了langchain-anthropic包到最新版本
2. **Settings类缺少save方法** - 修改了CLI代码，使用save_settings函数
3. **Agent为None的问题** - 添加了agent存在性检查，避免NoneType错误

## 下一步计划

1. 添加更多LLM提供商支持
2. 实现LLM提供商的性能监控
3. 添加LLM使用统计和成本跟踪
4. 实现LLM响应缓存机制