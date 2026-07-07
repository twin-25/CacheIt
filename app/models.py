from pydantic import BaseModel

class CacheRequest(BaseModel):
    model: str
    messages: list
    system: str | None = None
    max_tokens: int = 1000
    stream: bool = False
    temperature: float | None = None

class CacheResponse(BaseModel):
  answer: str
  cache_hit: bool