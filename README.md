# CortexPropel

An intelligent task management agent powered by LangGraph that helps you manage complex tasks more efficiently and intelligently.

## Features

- Natural language task entry and management
- Intelligent task decomposition and planning
- Task status tracking and updates
- Project visualization (Gantt charts, dependency graphs)
- CLI-based interaction
- Support for multiple LLM providers (OpenAI, Azure OpenAI, Anthropic, Cohere, Hugging Face, and custom endpoints)

## Installation

```bash
pip install cortex-propel
```

## Quick Start

```bash
# Initialize a new project
cortex-propel init

# Add a new task
cortex-propel add "Complete the quarterly report by Friday"

# Check your tasks
cortex-propel list

# Update task status
cortex-propel update task-123 status "in progress"
```

## LLM Provider Configuration

CortexPropel supports multiple LLM providers. By default, it uses OpenAI, but you can configure it to use other providers:

### Using Environment Variables

```bash
# For OpenAI (default)
export OPENAI_API_KEY="your-openai-api-key"

# For Anthropic Claude
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# For Azure OpenAI
export AZURE_OPENAI_API_KEY="your-azure-openai-api-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com/"

# For custom OpenAI-compatible endpoints
export CUSTOM_OPENAI_API_KEY="your-custom-api-key"
export CUSTOM_OPENAI_ENDPOINT="https://your-custom-endpoint.com/v1"
```

### Using Configuration File

Create or edit `~/.cortex_propel/config.json`:

```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 1000,
    "api_key": "your-api-key-here"
  }
}
```

For detailed instructions on configuring different LLM providers, see the [LLM Providers documentation](docs/llm_providers.md).

## Documentation

For detailed documentation, see the [docs](docs/) directory.

## Development

```bash
# Clone the repository
git clone https://github.com/cortexpropel/cortex-propel.git
cd cortex-propel

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
pytest
```

## License

MIT License - see the [LICENSE](LICENSE) file for details.