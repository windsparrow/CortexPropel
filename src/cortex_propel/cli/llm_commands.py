"""LLM provider management CLI commands."""

import json
import os
from typing import Dict, Any, Optional

import click
from rich.console import Console
from rich.table import Table

from ..config.settings import load_settings, save_settings
from ..llm import LLMProviderFactory

console = Console()


@click.group()
def llm():
    """Manage LLM provider configurations."""
    pass


@llm.command()
def list_providers():
    """List all supported LLM providers."""
    providers = LLMProviderFactory.get_supported_providers()
    
    table = Table(title="Supported LLM Providers")
    table.add_column("Provider", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Description", style="green")
    table.add_column("Environment Variable", style="yellow")
    
    for provider_id, provider_info in providers.items():
        env_vars = [provider_info["env_var"]]
        if "additional_env_vars" in provider_info:
            env_vars.extend(provider_info["additional_env_vars"])
        
        table.add_row(
            provider_id,
            provider_info["name"],
            provider_info["description"],
            ", ".join(env_vars)
        )
    
    console.print(table)


@llm.command()
def current():
    """Show current LLM provider configuration."""
    settings = load_settings()
    
    console.print(f"[bold]Current LLM Configuration[/bold]")
    console.print(f"Provider: {settings.llm.provider}")
    console.print(f"Model: {settings.llm.model}")
    console.print(f"Temperature: {settings.llm.temperature}")
    console.print(f"Max Tokens: {settings.llm.max_tokens}")
    
    if settings.llm.api_key:
        masked_key = settings.llm.api_key[:4] + "..." + settings.llm.api_key[-4:]
        console.print(f"API Key: {masked_key}")
    else:
        console.print("API Key: [red]Not configured[/red]")
    
    if settings.llm.api_base:
        console.print(f"API Base: {settings.llm.api_base}")
    
    if settings.llm.api_version:
        console.print(f"API Version: {settings.llm.api_version}")


@llm.command()
@click.argument("provider")
@click.option("--model", help="Model name")
@click.option("--api-key", help="API key")
@click.option("--api-base", help="API base URL")
@click.option("--api-version", help="API version")
@click.option("--temperature", type=float, help="Temperature")
@click.option("--max-tokens", type=int, help="Maximum tokens")
def configure(provider: str, model: Optional[str], api_key: Optional[str], 
             api_base: Optional[str], api_version: Optional[str],
             temperature: Optional[float], max_tokens: Optional[int]):
    """Configure LLM provider settings."""
    settings = load_settings()
    
    # Update provider
    settings.llm.provider = provider
    
    # Update other settings if provided
    if model:
        settings.llm.model = model
    if api_key:
        settings.llm.api_key = api_key
    if api_base:
        settings.llm.api_base = api_base
    if api_version:
        settings.llm.api_version = api_version
    if temperature is not None:
        settings.llm.temperature = temperature
    if max_tokens is not None:
        settings.llm.max_tokens = max_tokens
    
    # Save settings
    save_settings(settings)
    
    console.print(f"[green]Successfully configured {provider} provider[/green]")
    
    # Show updated configuration
    current()


@llm.command()
@click.argument("provider")
def models(provider: str):
    """List available models for a provider."""
    providers = LLMProviderFactory.get_supported_providers()
    
    if provider not in providers:
        console.print(f"[red]Provider '{provider}' not supported[/red]")
        return
    
    provider_info = providers[provider]
    models = provider_info.get("models", [])
    
    if not models:
        console.print(f"[yellow]No specific models listed for {provider_info['name']}[/yellow]")
        console.print("You can use any valid model name for this provider.")
        return
    
    table = Table(title=f"Available Models for {provider_info['name']}")
    table.add_column("Model", style="cyan")
    
    for model in models:
        table.add_row(model)
    
    console.print(table)


@llm.command()
@click.argument("provider")
def test(provider: str):
    """Test connection to an LLM provider."""
    settings = load_settings()
    
    # Temporarily update provider
    original_provider = settings.llm.provider
    settings.llm.provider = provider
    
    try:
        # Create LLM instance
        llm = LLMProviderFactory.create_llm(settings.llm)
        
        console.print(f"[green]Successfully connected to {provider}[/green]")
        console.print(f"Model: {settings.llm.model}")
    except Exception as e:
        console.print(f"[red]Failed to connect to {provider}: {str(e)}[/red]")
    finally:
        # Restore original provider
        settings.llm.provider = original_provider