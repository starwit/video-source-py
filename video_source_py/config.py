from pydantic import BaseModel, conint
from pydantic_settings import BaseSettings, SettingsConfigDict
from visionlib.pipeline.settings import LogLevel, YamlConfigSettingsSource


class RedisConfig(BaseModel):
    host: str = 'localhost'
    port: conint(ge=1, le=65536) = 6379
    output_stream_prefix: str = 'videosource'


class VideoSourceConfig(BaseSettings):
    id: str
    uri: str
    max_fps: conint(ge=0) = 0
    log_level: LogLevel = LogLevel.WARNING
    reconnect_backoff_time: float = 1
    redis: RedisConfig = RedisConfig()

    model_config = SettingsConfigDict(env_nested_delimiter='__')

    @classmethod
    def settings_customise_sources(cls, settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings):
        return (init_settings, env_settings, YamlConfigSettingsSource(settings_cls), file_secret_settings)