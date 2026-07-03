from pydantic import BaseModel

class CacheRequest(BaseModel):
  session_id: str
  question: str

class CacheResponse(BaseModel):
  answer: str
  cache_hit: bool