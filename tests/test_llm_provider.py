#!/usr/bin/env python3
"""
Test script for LLM provider management functionality.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cortex_propel.llm.llm_provider import LLMProviderFactory
from cortex_propel.config.settings import LLMSettings


class TestLLMProvider(unittest.TestCase):
    """Test cases for LLM provider functionality."""
    
    def test_get_supported_providers(self):
        """Test getting supported providers."""
        providers = LLMProviderFactory.get_supported_providers()
        
        # Check that expected providers are present
        self.assertIn("openai", providers)
        self.assertIn("azure", providers)
        self.assertIn("anthropic", providers)
        self.assertIn("cohere", providers)
        self.assertIn("huggingface", providers)
        self.assertIn("custom", providers)
        
        # Check provider structure
        for provider_id, provider_info in providers.items():
            self.assertIn("name", provider_info)
            self.assertIn("description", provider_info)
            self.assertIn("models", provider_info)
            self.assertIn("env_var", provider_info)
    
    def test_get_available_models(self):
        """Test getting available models for a provider."""
        # Test OpenAI models
        openai_models = LLMProviderFactory.get_available_models("openai")
        self.assertIn("gpt-3.5-turbo", openai_models)
        self.assertIn("gpt-4", openai_models)
        self.assertIn("gpt-4-turbo", openai_models)
        
        # Test Anthropic models
        anthropic_models = LLMProviderFactory.get_available_models("anthropic")
        self.assertIn("claude-3-opus-20240229", anthropic_models)
        self.assertIn("claude-3-sonnet-20240229", anthropic_models)
        self.assertIn("claude-3-haiku-20240307", anthropic_models)
        
        # Test non-existent provider
        unknown_models = LLMProviderFactory.get_available_models("unknown")
        self.assertEqual(unknown_models, [])
    
    def test_get_default_api_key(self):
        """Test getting default API key from environment."""
        # Test with environment variable set
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            api_key = LLMProviderFactory._get_default_api_key("openai")
            self.assertEqual(api_key, "test-key")
        
        # Test with no environment variable
        with patch.dict(os.environ, {}, clear=True):
            api_key = LLMProviderFactory._get_default_api_key("openai")
            self.assertIsNone(api_key)
    
    @patch('cortex_propel.llm.llm_provider.ChatOpenAI')
    def test_create_openai_llm(self, mock_chat_openai):
        """Test creating OpenAI LLM."""
        # Setup mock
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        # Create settings
        settings = LLMSettings(
            provider="openai",
            model="gpt-4",
            api_key="test-key",
            temperature=0.5,
            max_tokens=500
        )
        
        # Create LLM
        llm = LLMProviderFactory.create_llm(settings)
        
        # Verify mock was called with correct parameters
        mock_chat_openai.assert_called_once_with(
            model="gpt-4",
            api_key="test-key",
            temperature=0.5,
            max_tokens=500
        )
        
        # Verify returned LLM is the mock
        self.assertEqual(llm, mock_llm)
    
    def test_create_openai_llm_missing_api_key(self):
        """Test creating OpenAI LLM without API key raises error."""
        # Create settings without API key
        settings = LLMSettings(
            provider="openai",
            model="gpt-4"
        )
        
        # Verify error is raised
        with self.assertRaises(ValueError) as context:
            LLMProviderFactory.create_llm(settings)
        
        self.assertIn("API key is required", str(context.exception))
    
    @patch('cortex_propel.llm.llm_provider.ChatOpenAI')
    def test_create_azure_llm(self, mock_chat_openai):
        """Test creating Azure OpenAI LLM."""
        # Setup mock
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        # Create settings
        settings = LLMSettings(
            provider="azure",
            model="gpt-4",
            api_key="test-key",
            temperature=0.5,
            max_tokens=500
        )
        
        # Mock environment variables
        with patch.dict(os.environ, {
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_API_VERSION": "2023-05-15"
        }):
            # Create LLM
            llm = LLMProviderFactory.create_llm(settings)
        
        # Verify mock was called with correct parameters
        mock_chat_openai.assert_called_once_with(
            model="gpt-4",
            api_key="test-key",
            azure_endpoint="https://test.openai.azure.com/",
            api_version="2023-05-15",
            temperature=0.5,
            max_tokens=500
        )
        
        # Verify returned LLM is the mock
        self.assertEqual(llm, mock_llm)
    
    @patch('cortex_propel.llm.llm_provider.ChatOpenAI')
    def test_create_custom_llm(self, mock_chat_openai):
        """Test creating custom OpenAI-compatible LLM."""
        # Setup mock
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        # Create settings
        settings = LLMSettings(
            provider="custom",
            model="custom-model",
            api_key="test-key",
            temperature=0.5,
            max_tokens=500
        )
        
        # Mock environment variables
        with patch.dict(os.environ, {
            "CUSTOM_OPENAI_ENDPOINT": "https://api.example.com/v1"
        }):
            # Create LLM
            llm = LLMProviderFactory.create_llm(settings)
        
        # Verify mock was called with correct parameters
        mock_chat_openai.assert_called_once_with(
            model="custom-model",
            api_key="test-key",
            base_url="https://api.example.com/v1",
            temperature=0.5,
            max_tokens=500
        )
        
        # Verify returned LLM is the mock
        self.assertEqual(llm, mock_llm)
    
    def test_unsupported_provider(self):
        """Test creating LLM with unsupported provider raises error."""
        # Create settings with unsupported provider
        settings = LLMSettings(
            provider="unsupported",
            model="test-model",
            api_key="test-key"
        )
        
        # Verify error is raised
        with self.assertRaises(ValueError) as context:
            LLMProviderFactory.create_llm(settings)
        
        self.assertIn("Unsupported provider", str(context.exception))


if __name__ == "__main__":
    unittest.main()