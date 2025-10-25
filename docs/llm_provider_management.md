# LLM Provider Management in CortexPropel

CortexPropel supports multiple LLM providers, allowing you to choose the best model for your needs. This document explains how to configure and use different LLM providers.

## Supported Providers

CortexPropel currently supports the following LLM providers:

1. **OpenAI** - OpenAI's GPT models (gpt-3.5-turbo, gpt-4, gpt-4-turbo)
2. **Azure OpenAI** - Azure OpenAI Service
3. **Anthropic** - Anthropic's Claude models
4. **Cohere** - Cohere's models
5. **Hugging Face** - Hugging Face models
6. **Custom** - Any OpenAI-compatible API endpoint

## Configuration

### Using the CLI

You can manage LLM providers using the CLI:

```bash
# List all supported providers
python -m src.cortex_propel.cli.main llm list

# List available models for a provider
python -m src.cortex_propel.cli.main llm models openai

# Show current LLM configuration
python -m src.cortex_propel.cli.main llm current

# Configure a new provider
python -m src.cortex_propel.cli.main llm configure openai --model gpt-4 --api-key your-api-key

# Test connection to a provider
python -m src.cortex_propel.cli.main llm test openai
```

### Using a Configuration File

You can also configure LLM providers using a JSON configuration file:

```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000,
    "api_key": "your-api-key-here"
  },
  "storage": {
    "data_dir": "~/.cortex_propel"
  },
  "cli": {
    "default_project": "personal"
  }
}
```

Save this file as `~/.cortex_propel/config.json` or specify a custom path using the `--config` flag.

### Using Environment Variables

You can use environment variables to configure API keys:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export AZURE_OPENAI_API_KEY="your-azure-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export COHERE_API_KEY="your-cohere-api-key"
export HUGGINGFACEHUB_API_TOKEN="your-huggingface-token"
export CUSTOM_OPENAI_API_KEY="your-custom-api-key"

# For Azure and Custom providers
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_VERSION="2023-05-15"
export CUSTOM_OPENAI_ENDPOINT="https://api.example.com/v1"
```

## Provider-Specific Configuration

### OpenAI

```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "your-openai-api-key"
  }
}
```

### Azure OpenAI

```json
{
  "llm": {
    "provider": "azure",
    "model": "gpt-4",
    "api_key": "your-azure-api-key",
    "api_base": "https://your-resource.openai.azure.com/",
    "api_version": "2023-05-15"
  }
}
```

### Anthropic

```json
{
  "llm": {
    "provider": "anthropic",
    "model": "claude-3-opus-20240229",
    "api_key": "your-anthropic-api-key"
  }
}
```

### Cohere

```json
{
  "llm": {
    "provider": "cohere",
    "model": "command",
    "api_key": "your-cohere-api-key"
  }
}
```

### Hugging Face

```json
{
  "llm": {
    "provider": "huggingface",
    "model": "meta-llama/Llama-2-70b-chat-hf",
    "api_key": "your-huggingface-token"
  }
}
```

### Custom OpenAI-Compatible

```json
{
  "llm": {
    "provider": "custom",
    "model": "custom-model",
    "api_key": "your-api-key",
    "api_base": "https://api.example.com/v1"
  }
}
```

## Programmatic Usage

You can also use the LLM provider management programmatically:

```python
from cortex_propel.llm.llm_provider import LLMProviderFactory
from cortex_propel.config.settings import LLMSettings

# Create settings for OpenAI
settings = LLMSettings(
    provider="openai",
    model="gpt-4",
    api_key="your-api-key"
)

# Create LLM instance
llm = LLMProviderFactory.create_llm(settings)

# Use the LLM
response = llm.invoke("Hello, how are you?")
print(response.content)
```

## Switching Between Providers

You can easily switch between providers by changing the `provider` field in your configuration or by using the CLI:

```bash
# Switch to Anthropic
python -m src.cortex_propel.cli.main llm configure anthropic --model claude-3-sonnet-20240229

# Switch to Azure OpenAI
python -m src.cortex_propel.cli.main llm configure azure --model gpt-4 --api-base https://your-resource.openai.azure.com/
```

## Best Practices

1. **Use Environment Variables for API Keys**: Avoid hardcoding API keys in configuration files. Use environment variables instead.

2. **Choose the Right Model for the Task**: 
   - For simple tasks, use faster models like gpt-3.5-turbo
   - For complex reasoning tasks, use more powerful models like gpt-4 or claude-3-opus

3. **Adjust Temperature and Max Tokens**:
   - Lower temperature (0.1-0.3) for more deterministic responses
   - Higher temperature (0.7-1.0) for more creative responses
   - Adjust max_tokens based on the expected response length

4. **Test Your Configuration**: Always test your configuration before using it in production:

```bash
python -m src.cortex_propel.cli.main llm test openai
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Make sure your API key is correctly set and has the necessary permissions.

2. **Model Not Available**: Check if the model you're trying to use is available in your region or with your subscription.

3. **Connection Errors**: Verify your internet connection and API endpoint URLs.

4. **Import Errors**: Make sure you have the required packages installed:

```bash
pip install langchain-openai langchain-anthropic langchain-community
```

### Getting Help

If you encounter issues with LLM provider configuration:

1. Check the error messages for specific details
2. Verify your API keys and endpoints
3. Test your configuration using the CLI test command
4. Consult the documentation for your specific LLM provider