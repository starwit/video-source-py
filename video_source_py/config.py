from pydantic import BaseModel

class VideoSourceConfig(BaseModel):
    id: str
    name: str
    uri: str
    use_source_fps: bool = False