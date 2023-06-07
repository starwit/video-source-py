from enum import Enum

from pydantic import BaseModel

class LogLevel(str, Enum):
    CRITICAL = 'CRITICAL'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'

class VideoSourceConfig(BaseModel):
    id: str
    uri: str
    use_source_fps: bool = False
    log_level: LogLevel = LogLevel.WARNING
    reconnect_backoff_time: float = 1