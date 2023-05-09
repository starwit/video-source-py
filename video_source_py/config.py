from pydantic import BaseModel

class VideoSourceConfig(BaseModel):
    id: str
    name: str
    uri: str