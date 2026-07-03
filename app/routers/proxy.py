from anthropic import Anthropic
from app.services.cache_engine import store_in_cache, create_session_index, delete_session_index, search_cache
from app.config import ANTHROPIC_API_KEY
from fastapi import APIRouter, HTTPException
from app.models import CacheRequest, CacheResponse

router = APIRouter()

client = Anthropic(api_key=ANTHROPIC_API_KEY)

@router.post('/session/{session_id}')
def create_session_cache(session_id: str):
  try:
    return create_session_index(session_id)
  except RuntimeError:
    raise HTTPException(status_code=503, detail="Redis is down")
  
@router.delete('/session/{session_id}')
def delete_session_cache(session_id: str):
  try:
    delete_session_index(session_id)
    return {"detail": "Session cache deleted"}

  except RuntimeError:
    raise HTTPException(status_code=503, detail="Failed to delete session cache")
  

@router.post('/v1/messages')
def proxy_request(request: CacheRequest) -> CacheResponse:
  search = search_cache(request.session_id, request.question)
  if search is not None:
    return CacheResponse(answer=search, cache_hit=True)

  try:
    response = client.messages.create(
      model="claude-haiku-20240307",
      max_tokens=1000,
      system=request.system or "you are a helpful assistant.",
      messages=request.messages
    )
    answer = response.content[0].text
  except Exception as e:
    raise HTTPException(status_code=503, detail=f"LLM call failed: {e}")

  store_in_cache(request.session_id, request.question, answer)

  return CacheResponse(answer=answer, cache_hit=False)
    
  
    