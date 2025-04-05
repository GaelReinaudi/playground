#!/usr/bin/env python3
"""
Global settings for the project, loaded from environment variables.
Uses pydantic-settings to manage configuration with .env file support.
"""

import os
from pathlib import Path
from typing import ClassVar, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Find the closest .env file by searching up the directory tree
def find_env_file():
    """Find the closest .env file by looking in current dir and all parent dirs."""
    current_dir = Path.cwd()
    while current_dir != current_dir.parent:  # Stop at root
        env_file = current_dir / ".env"
        if env_file.exists():
            return str(env_file)
        current_dir = current_dir.parent
    return ".env"  # Default fallback


# Use the detected .env file path
ENV_FILE_PATH = find_env_file()


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Automatically loads values from .env file if present.
    """

    # OpenAI API settings
    openai_api_key: str = Field(default="", description="OpenAI API key for accessing the API")
    openai_model: str = Field(default="gpt-4o-2024-08-06", description="OpenAI model to use for API calls")
    openai_temperature: float = Field(default=0.0, description="Temperature for OpenAI API calls")

    # Phoenix telemetry settings
    phoenix_enabled: bool = Field(default=True, description="Whether Phoenix telemetry is enabled")
    phoenix_project_name: str = Field(
        default="llm-tricks-01-json-schema", description="Project name for Phoenix telemetry"
    )

    # Phoenix headers and endpoints
    otel_exporter_otlp_headers: str = Field(default="", description="OTEL exporter headers")
    phoenix_client_headers: str = Field(default="", description="Phoenix client headers")
    phoenix_collector_endpoint: str = Field(default="", description="Phoenix collector endpoint")

    # Path settings
    generated_dir: str = Field(default="generated", description="Directory to store generated files")

    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_key(cls, v: str) -> str:
        """Validate that the OpenAI API key is properly formatted."""
        if v and not v.startswith("sk-"):
            raise ValueError("OpenAI API key must start with 'sk-'")
        return v

    # Use the closest .env file
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, env_file_encoding="utf-8", env_prefix="", case_sensitive=False, extra="ignore"
    )

    def setup_phoenix_environment(self):
        """
        Set up Phoenix environment variables based on the loaded settings.
        Phoenix requires these to be set as actual environment variables.
        """
        if self.phoenix_enabled:
            # Set the Phoenix environment variables
            os.environ["PHOENIX_CLIENT_HEADERS"] = self.phoenix_client_headers
            os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = self.phoenix_collector_endpoint
            os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = self.otel_exporter_otlp_headers

            # Log what we're doing
            print("Phoenix environment variables set:")
            print(f"  PHOENIX_COLLECTOR_ENDPOINT: {self.phoenix_collector_endpoint}")
            # Don't print the actual API key for security
            print("  PHOENIX_CLIENT_HEADERS: api_key=****")
            print("  OTEL_EXPORTER_OTLP_HEADERS: api_key=****")
        else:
            print("Phoenix telemetry is disabled. Not setting environment variables.")


if __name__ == "__main__":
    """
    When run directly, display the current settings (good for debugging).
    Hides the API key for security.
    """
    settings = Settings()
    settings_dict = settings.model_dump()
    if "openai_api_key" in settings_dict:
        api_key = settings_dict["openai_api_key"]
        if api_key:
            # Show only first and last 4 characters
            masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "****"
            settings_dict["openai_api_key"] = masked_key

    # Also mask Phoenix API keys for security
    for key in ["phoenix_client_headers", "otel_exporter_otlp_headers"]:
        if settings_dict.get(key):
            settings_dict[key] = "api_key=****"

    import json

    print("Current settings:")
    print(json.dumps(settings_dict, indent=2))
    print(f"Using .env file from: {ENV_FILE_PATH}")

    # Show current OS environment variables for Phoenix
    print("\nCurrent Phoenix environment variables:")
    for env_var in ["PHOENIX_CLIENT_HEADERS", "PHOENIX_COLLECTOR_ENDPOINT", "OTEL_EXPORTER_OTLP_HEADERS"]:
        value = os.environ.get(env_var, "Not set")
        # Mask API keys for security
        if "api_key" in value:
            value = "api_key=****"
        print(f"  {env_var}: {value}")
