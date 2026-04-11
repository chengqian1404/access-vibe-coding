from datetime import datetime
from typing import Any, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config.settings import settings
from app.config.llm_config import LLM_PROVIDERS, get_active_provider_config
from app.models.recording import Base
from app.models.config import AppConfig
from app.utils.logger import logger


_engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)
_SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)


def _get_session() -> Session:
    return _SessionLocal()


class ConfigManager:
    """Persist and retrieve application configuration from SQLite."""

    def get(self, key: str, default: Any = None) -> Any:
        session = _get_session()
        try:
            record = session.query(AppConfig).filter(AppConfig.key == key).first()
            if record is None:
                return default
            return record.value
        except Exception as exc:
            logger.error("ConfigManager.get error for key=%s: %s", key, exc)
            return default
        finally:
            session.close()

    def set(self, key: str, value: Any) -> None:
        session = _get_session()
        try:
            record = session.query(AppConfig).filter(AppConfig.key == key).first()
            if record:
                record.value = str(value) if value is not None else None
                record.updated_at = datetime.utcnow()
            else:
                record = AppConfig(key=key, value=str(value) if value is not None else None)
                session.add(record)
            session.commit()
        except Exception as exc:
            session.rollback()
            logger.error("ConfigManager.set error for key=%s: %s", key, exc)
        finally:
            session.close()

    def get_all(self) -> dict:
        session = _get_session()
        try:
            records = session.query(AppConfig).all()
            return {r.key: r.value for r in records}
        except Exception as exc:
            logger.error("ConfigManager.get_all error: %s", exc)
            return {}
        finally:
            session.close()

    def save_weixin_id(self, weixin_id: str) -> None:
        self.set("weixin_id", weixin_id)

    def get_weixin_id(self) -> Optional[str]:
        return self.get("weixin_id")

    def get_llm_config(self) -> dict:
        provider = self.get("llm_provider", settings.LLM_PROVIDER)
        provider_cfg = LLM_PROVIDERS.get(provider, LLM_PROVIDERS["qwen"]).copy()

        stored_key = self.get(f"{provider}_api_key")
        if stored_key:
            provider_cfg["api_key"] = stored_key

        stored_base_url = self.get(f"{provider}_base_url")
        if stored_base_url:
            provider_cfg["base_url"] = stored_base_url

        provider_cfg["provider"] = provider
        return provider_cfg

    def update_from_dict(self, data: dict) -> None:
        for key, value in data.items():
            self.set(key, value)


config_manager = ConfigManager()
