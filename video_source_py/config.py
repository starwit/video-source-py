from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated
from visionlib.pipeline.settings import LogLevel, YamlConfigSettingsSource


class RedisConfig(BaseModel):
    host: str = 'localhost'
    port: Annotated[int, Field(ge=1, le=65536)] = 6379
    output_stream_prefix: str = 'videosource'

class PositionConfiguration(BaseModel):
    stream_id: str = "positionsource:self"
    max_position_skew: int = 1500
    add_position_to_frame: bool = True
    drop_frames_if_no_position: bool = False    

class VideoSourceConfig(BaseSettings):
    id: str
    uri: str
    max_fps: Annotated[int, Field(ge=0)] = 0
    jpeg_encode: bool = True
    jpeg_quality: Annotated[int, Field(ge=0, le=100)] = 80
    scale_width: Annotated[int, Field(ge=0)] = 0
    mask_path: Optional[Path] = None
    log_level: LogLevel = LogLevel.WARNING
    reconnect_backoff_time: float = 1
    position_configuration: PositionConfiguration = PositionConfiguration()
    redis: RedisConfig = RedisConfig()
    prometheus_port: Annotated[int, Field(gt=1024, le=65536)] = 8000

    model_config = SettingsConfigDict(env_nested_delimiter='__')

    @classmethod
    def settings_customise_sources(cls, settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings):
        return (init_settings, env_settings, YamlConfigSettingsSource(settings_cls), file_secret_settings)