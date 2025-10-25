#!/usr/bin/env python3
"""
Example script demonstrating LLM provider management in CortexPropel.
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cortex_propel.llm.llm_provider import LLMProviderFactory
from cortex_propel.config.settings import LLMSettings


def main():
    """Demonstrate LLM provider management."""
    
    print("=== CortexPropel LLM Provider Management Demo ===\n")
    
    # 1. List all supported providers
    print("1. Supported LLM providers:")
    providers = LLMProviderFactory.get_supported_providers()
    for provider_id, provider_info in providers.items():
        print(f"   - {provider_id}: {provider_info['name']} - {provider_info['description']}")
    print()
    
    # 2. List available models for a specific provider
    print("2. Available models for OpenAI:")
    openai_models = LLMProviderFactory.get_available_models("openai")
    for model in openai_models:
        print(f"   - {model}")
    print()
    
    # 3. Create LLM instances for different providers
    print("3. Creating LLM instances:")
    
    # OpenAI LLM (requires API key)
    try:
        openai_settings = LLMSettings(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key=os.environ.get("OPENAI_API_KEY", "your-api-key-here")
        )
        openai_llm = LLMProviderFactory.create_llm(openai_settings)
        print("   ✓ OpenAI LLM created successfully")
    except Exception as e:
        print(f"   ✗ Failed to create OpenAI LLM: {e}")
    
    # Anthropic LLM (requires API key)
    try:
        anthropic_settings = LLMSettings(
            provider="anthropic",
            model="claude-3-haiku-20240307",
            api_key=os.environ.get("ANTHROPIC_API_KEY", "your-api-key-here")
        )
        anthropic_llm = LLMProviderFactory.create_llm(anthropic_settings)
        print("   ✓ Anthropic LLM created successfully")
    except Exception as e:
        print(f"   ✗ Failed to create Anthropic LLM: {e}")
    
    # Custom LLM (for demonstration)
    try:
        custom_settings = LLMSettings(
            provider="custom",
            model="custom-model",
            api_key="custom-api-key",
            api_base="https://api.example.com/v1"
        )
        custom_llm = LLMProviderFactory.create_llm(custom_settings)
        print("   ✓ Custom LLM created successfully")
    except Exception as e:
        print(f"   ✗ Failed to create Custom LLM: {e}")
    
    print("\n=== Demo completed ===")


if __name__ == "__main__":
    main()