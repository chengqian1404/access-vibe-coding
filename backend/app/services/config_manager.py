"""
Config Manager - Manages application configuration and API key storage
"""
import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet
from loguru import logger


class ConfigManager:
    """Manages application configuration with encrypted API key storage."""

    def __init__(self):
        self.config_dir = Path(os.path.expanduser("~/.access-vibe-coding"))
        self.config_file = self.config_dir / "config.json"
        self.key_file = self.config_dir / ".key"
        self._config: Dict[str, Any] = {}
        self._fernet: Optional[Fernet] = None

        self._ensure_config_dir()
        self._load_or_create_key()
        self._load_config()

    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load_or_create_key(self):
        """Load or generate encryption key."""
        try:
            if self.key_file.exists():
                with open(self.key_file, "rb") as f:
                    key = f.read()
            else:
                key = Fernet.generate_key()
                with open(self.key_file, "wb") as f:
                    f.write(key)
                # Set restrictive permissions on Unix
                if os.name != "nt":
                    os.chmod(self.key_file, 0o600)

            self._fernet = Fernet(key)
        except Exception as e:
            logger.warning(f"Failed to initialize encryption: {e}. API keys will be stored in plaintext.")
            self._fernet = None

    def _load_config(self):
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
            else:
                self._config = {"providers": {}, "default_provider": "openai", "settings": {}}
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self._config = {"providers": {}, "default_provider": "openai", "settings": {}}

    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def _encrypt(self, value: str) -> str:
        """Encrypt a string value."""
        if self._fernet and value:
            return self._fernet.encrypt(value.encode()).decode()
        return value

    def _decrypt(self, value: str) -> str:
        """Decrypt a string value."""
        if self._fernet and value:
            try:
                return self._fernet.decrypt(value.encode()).decode()
            except Exception:
                # If decryption fails, return as-is (might be unencrypted)
                return value
        return value

    def set_provider_config(
        self,
        provider: str,
        api_key: str,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """Save provider configuration with encrypted API key."""
        if "providers" not in self._config:
            self._config["providers"] = {}

        provider_config = {
            "api_key": self._encrypt(api_key),
            "api_key_set": bool(api_key),
        }

        if base_url:
            provider_config["base_url"] = base_url
        if model:
            provider_config["model"] = model

        self._config["providers"][provider] = provider_config
        self._save_config()
        logger.info(f"Saved config for provider: {provider}")

    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get provider configuration with decrypted API key."""
        providers = self._config.get("providers", {})
        provider_config = providers.get(provider, {})

        result = dict(provider_config)
        if "api_key" in result:
            result["api_key"] = self._decrypt(result["api_key"])

        return result

    def get_default_provider(self) -> str:
        """Get the default LLM provider."""
        return self._config.get("default_provider", "openai")

    def set_default_provider(self, provider: str):
        """Set the default LLM provider."""
        self._config["default_provider"] = provider
        self._save_config()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get an application setting."""
        return self._config.get("settings", {}).get(key, default)

    def set_setting(self, key: str, value: Any):
        """Set an application setting."""
        if "settings" not in self._config:
            self._config["settings"] = {}
        self._config["settings"][key] = value
        self._save_config()

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all application settings."""
        return {
            "default_provider": self.get_default_provider(),
            "providers": {
                provider: {
                    "api_key_set": config.get("api_key_set", False),
                    "base_url": config.get("base_url"),
                    "model": config.get("model"),
                }
                for provider, config in self._config.get("providers", {}).items()
            },
            "settings": self._config.get("settings", {}),
        }

    def delete_provider_config(self, provider: str) -> bool:
        """Delete provider configuration."""
        if provider in self._config.get("providers", {}):
            del self._config["providers"][provider]
            self._save_config()
            return True
        return False
