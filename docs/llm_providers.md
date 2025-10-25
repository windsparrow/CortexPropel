# 配置不同的LLM提供商

CortexPropel支持多种LLM提供商，包括OpenAI、Azure OpenAI、Anthropic、Cohere、Hugging Face以及任何OpenAI兼容的自定义端点。

## 配置方法

### 1. 使用配置文件

创建或编辑 `~/.cortex_propel/config.json` 文件，使用以下格式：

```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 1000,
    "api_key": "your-api-key-here"
  },
  "storage": {
    "data_dir": "~/.cortex_propel",
    "backup_enabled": true,
    "backup_frequency": "daily",
    "max_backups": 10
  },
  "cli": {
    "default_project": "personal",
    "output_format": "text",
    "confirm_destructive_actions": true
  }
}
```

### 2. 使用环境变量

您也可以使用环境变量来配置LLM提供商：

#### OpenAI
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

#### Azure OpenAI
```bash
export AZURE_OPENAI_API_KEY="your-azure-openai-api-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com/"
export AZURE_OPENAI_API_VERSION="2023-12-01-preview"
```

#### Anthropic Claude
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

#### Cohere
```bash
export COHERE_API_KEY="your-cohere-api-key"
```

#### Hugging Face
```bash
export HUGGINGFACEHUB_API_TOKEN="your-huggingface-token"
```

#### 自定义OpenAI兼容端点
```bash
export CUSTOM_OPENAI_API_KEY="your-custom-api-key"
export CUSTOM_OPENAI_ENDPOINT="https://your-custom-endpoint.com/v1"
```

## 支持的提供商和模型

### OpenAI
- 提供商: `openai`
- 支持的模型: `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo` 等

### Azure OpenAI
- 提供商: `azure`
- 支持的模型: `gpt-35-turbo`, `gpt-4` 等
- 需要额外配置: `api_base`, `api_version`

### Anthropic
- 提供商: `anthropic`
- 支持的模型: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-3-haiku-20240307` 等

### Cohere
- 提供商: `cohere`
- 支持的模型: `command`, `command-nightly`, `command-light` 等

### Hugging Face
- 提供商: `huggingface`
- 支持的模型: `meta-llama/Llama-2-70b-chat-hf`, `mistralai/Mixtral-8x7B-Instruct-v0.1` 等

### 自定义端点
- 提供商: `custom`
- 支持任何OpenAI兼容的API端点
- 需要额外配置: `api_base`

## 示例配置文件

您可以在 `config_examples/` 目录中找到各种提供商的示例配置文件：

- `openai_config.json` - OpenAI配置示例
- `azure_config.json` - Azure OpenAI配置示例
- `anthropic_config.json` - Anthropic配置示例
- `custom_config.json` - 自定义端点配置示例

## 切换提供商

要切换LLM提供商，只需修改配置文件中的 `provider` 字段，或者设置相应的环境变量，然后重启CortexPropel即可。