import json
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class LLMSettings(BaseModel):
    """LLM configuration settings."""
    provider: str = Field(default="openai", description="LLM provider (openai, azure, anthropic, cohere, huggingface, custom)")
    model: str = Field(default="gpt-3.5-turbo", description="LLM model name")
    temperature: float = Field(default=0.7, description="LLM temperature")
    max_tokens: int = Field(default=1000, description="Maximum tokens to generate")
    api_key: Optional[str] = Field(default=None, description="API key for the LLM provider")
    api_base: Optional[str] = Field(default=None, description="API base URL for custom providers")
    api_version: Optional[str] = Field(default=None, description="API version for Azure OpenAI")


class StorageSettings(BaseModel):
    """Storage configuration settings."""
    data_dir: str = Field(default="~/.cortex_propel", description="Data directory path")
    backup_enabled: bool = Field(default=True, description="Enable automatic backups")
    backup_frequency: str = Field(default="daily", description="Backup frequency")
    max_backups: int = Field(default=10, description="Maximum number of backups to keep")


class CLISettings(BaseModel):
    """CLI configuration settings."""
    default_project: str = Field(default="personal", description="Default project ID")
    output_format: str = Field(default="text", description="Output format")
    confirm_destructive_actions: bool = Field(default=True, description="Confirm destructive actions")


class Settings(BaseModel):
    """Main configuration settings."""
    llm: LLMSettings = Field(default_factory=LLMSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    cli: CLISettings = Field(default_factory=CLISettings)


def load_settings(config_path: Optional[str] = None) -> Settings:
    """Load settings from a configuration file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Settings object
    """
    if config_path is None:
        # Default config path
        config_path = os.path.expanduser("~/.cortex_propel/config.json")
    
    # Default settings
    settings = Settings()
    
    # Load from file if it exists
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)
            
            # Update settings with loaded data
            settings = Settings(**config_data)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    # Override with environment variables
    if os.environ.get("OPENAI_API_KEY"):
        settings.llm.api_key = os.environ.get("OPENAI_API_KEY")
    
    if os.environ.get("AZURE_OPENAI_API_KEY"):
        settings.llm.api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    
    if os.environ.get("ANTHROPIC_API_KEY"):
        settings.llm.api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if os.environ.get("COHERE_API_KEY"):
        settings.llm.api_key = os.environ.get("COHERE_API_KEY")
    
    if os.environ.get("HUGGINGFACEHUB_API_TOKEN"):
        settings.llm.api_key = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    
    if os.environ.get("CUSTOM_OPENAI_API_KEY"):
        settings.llm.api_key = os.environ.get("CUSTOM_OPENAI_API_KEY")
    
    if os.environ.get("AZURE_OPENAI_ENDPOINT"):
        settings.llm.api_base = os.environ.get("AZURE_OPENAI_ENDPOINT")
    
    if os.environ.get("CUSTOM_OPENAI_ENDPOINT"):
        settings.llm.api_base = os.environ.get("CUSTOM_OPENAI_ENDPOINT")
    
    if os.environ.get("AZURE_OPENAI_API_VERSION"):
        settings.llm.api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
    
    if os.environ.get("CORTEX_PROPEL_DATA_DIR"):
        settings.storage.data_dir = os.environ.get("CORTEX_PROPEL_DATA_DIR")
    
    return settings


def save_settings(settings: Settings, config_path: Optional[str] = None) -> None:
    """Save settings to a configuration file.
    
    Args:
        settings: Settings object to save
        config_path: Path to the configuration file
    """
    if config_path is None:
        # Default config path
        config_path = os.path.expanduser("~/.cortex_propel/config.json")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # Save to file
    with open(config_path, "w") as f:
        json.dump(settings.dict(), f, indent=2)