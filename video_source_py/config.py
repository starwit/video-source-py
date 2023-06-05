from pydantic import BaseModel
from enum import Enum

class LogLevel(str, Enum):
    CRITICAL = 'CRITICAL'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'

class VideoSourceConfig(BaseModel):
    id: str
    name: str
    uri: str
    use_source_fps: bool = False
    log_level: LogLevel = LogLevel.WARNING