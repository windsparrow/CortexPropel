"""LLM provider factory for CortexPropel."""

import os
from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI
try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    from langchain_community.chat_models import ChatAnthropic
from langchain_community.chat_models import ChatCohere
from langchain_community.chat_models.huggingface import ChatHuggingFace

from ..config.settings import LLMSettings


class LLMProviderFactory:
    """Factory class for creating LLM instances based on provider settings."""
    
    @staticmethod
    def create_llm(settings: LLMSettings) -> Any:
        """Create an LLM instance based on the provider settings.
        
        Args:
            settings: LLM configuration settings
            
        Returns:
            An LLM instance compatible with LangChain
        """
        provider = settings.provider.lower()
        
        # Ensure API key is set
        api_key = settings.api_key or LLMProviderFactory._get_default_api_key(provider)
        
        if not api_key:
            raise ValueError(f"API key is required for provider: {provider}")
        
        if provider == "openai":
            return ChatOpenAI(
                model=settings.model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                api_key=api_key
            )
        
        elif provider == "azure":
            # Azure OpenAI
            return ChatOpenAI(
                model=settings.model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                api_key=api_key,
                azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
                api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
            )
        
        elif provider == "anthropic":
            try:
                # Try using the new langchain_anthropic package
                return ChatAnthropic(
                    model=settings.model,
                    temperature=settings.temperature,
                    max_tokens=settings.max_tokens,
                    api_key=api_key
                )
            except (TypeError, AttributeError, ValueError) as e:
                # Fallback to older langchain_community version with different parameter names
                if "anthropic_api_key" in str(e):
                    # If the error mentions anthropic_api_key, use that parameter name
                    return ChatAnthropic(
                        model=settings.model,
                        temperature=settings.temperature,
                        max_tokens=settings.max_tokens,
                        anthropic_api_key=api_key
                    )
                else:
                    # Otherwise re-raise the exception
                    raise
        
        elif provider == "cohere":
            return ChatCohere(
                model=settings.model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                cohere_api_key=api_key
            )
        
        elif provider == "huggingface":
            return ChatHuggingFace(
                repo_id=settings.model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                huggingfacehub_api_key=api_key
            )
        
        elif provider == "custom":
            # Custom OpenAI-compatible endpoint
            return ChatOpenAI(
                model=settings.model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                api_key=api_key,
                base_url=os.environ.get("CUSTOM_OPENAI_ENDPOINT")
            )
        
        else:
            # Raise error for unknown providers
            raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def _get_default_api_key(provider: str) -> Optional[str]:
        """Get the default API key for a provider from environment variables.
        
        Args:
            provider: The LLM provider name
            
        Returns:
            The API key if found, None otherwise
        """
        provider = provider.lower()
        
        env_var_map = {
            "openai": "OPENAI_API_KEY",
            "azure": "AZURE_OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "cohere": "COHERE_API_KEY",
            "huggingface": "HUGGINGFACEHUB_API_TOKEN",
            "custom": "CUSTOM_OPENAI_API_KEY"
        }
        
        env_var = env_var_map.get(provider)
        return os.environ.get(env_var) if env_var else None
    
    @staticmethod
    def get_supported_providers() -> Dict[str, Dict[str, Any]]:
        """Get a dictionary of supported LLM providers.
        
        Returns:
            Dictionary mapping provider names to their configurations
        """
        return {
            "openai": {
                "name": "OpenAI",
                "description": "OpenAI's GPT models",
                "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                "env_var": "OPENAI_API_KEY"
            },
            "azure": {
                "name": "Azure OpenAI",
                "description": "Azure OpenAI Service",
                "models": ["gpt-35-turbo", "gpt-4"],
                "env_var": "AZURE_OPENAI_API_KEY",
                "additional_env_vars": ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_VERSION"]
            },
            "anthropic": {
                "name": "Anthropic",
                "description": "Anthropic's Claude models",
                "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                "env_var": "ANTHROPIC_API_KEY"
            },
            "cohere": {
                "name": "Cohere",
                "description": "Cohere's models",
                "models": ["command", "command-nightly", "command-light"],
                "env_var": "COHERE_API_KEY"
            },
            "huggingface": {
                "name": "Hugging Face",
                "description": "Hugging Face models",
                "models": ["meta-llama/Llama-2-70b-chat-hf", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
                "env_var": "HUGGINGFACEHUB_API_TOKEN"
            },
            "custom": {
                "name": "Custom OpenAI-compatible",
                "description": "Any OpenAI-compatible API endpoint",
                "models": ["custom-model"],
                "env_var": "CUSTOM_OPENAI_API_KEY",
                "additional_env_vars": ["CUSTOM_OPENAI_ENDPOINT"]
            }
        }
    
    @staticmethod
    def get_available_models(provider: str) -> List[str]:
        """Get available models for a provider.
        
        Args:
            provider: The LLM provider name
            
        Returns:
            List of available models
        """
        provider = provider.lower()
        supported_providers = LLMProviderFactory.get_supported_providers()
        
        if provider in supported_providers:
            return supported_providers[provider].get("models", [])
        
        return []