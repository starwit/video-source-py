import os
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseSettings, BaseModel, conint


def yaml_config_settings_source(settings: BaseSettings) -> dict[str, Any]:
    return yaml.load(Path(os.environ.get('SETTINGS_FILE', 'settings.yaml')).read_text('utf-8'), Loader=yaml.Loader)


class LogLevel(str, Enum):
    CRITICAL = 'CRITICAL'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'


class RedisConfig(BaseModel):
    host: str
    port: conint(ge=1, le=65536)


class VideoSourceConfig(BaseSettings):
    id: str
    uri: str
    use_source_fps: bool = False
    log_level: LogLevel = LogLevel.WARNING
    reconnect_backoff_time: float = 1
    redis: RedisConfig = None

    class Config:
        env_nested_delimiter = '__'
        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (init_settings, env_settings, yaml_config_settings_source, file_secret_settings)