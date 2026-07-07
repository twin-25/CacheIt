from anthropic import Anthropic
from app.services.cache_engine import store_in_cache, create_session_index, delete_session_index, search_cache
from app.config import ANTHROPIC_API_KEY
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from app.models import CacheRequest, CacheResponse
from app.metrics import cache_hits_total, cache_misses_total, llm_duration_seconds
import time

router = APIRouter()

client = Anthropic(api_key=ANTHROPIC_API_KEY)

@router.post('/session/{session_id}')
def create_session_cache(session_id: str):
  try:
    create_session_index(session_id)
    return {"detail": f"Session {session_id} cache created"}
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
def proxy_request(request: CacheRequest, x_session_id: Optional[str] = Header(None)):
    question = ""
    print(f"Full messages received: {request.messages}")
    for msg in reversed(request.messages):
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if isinstance(content, list):
                for block in content:
                    if block.get("type") == "text":
                        question = block.get("text", "")
            else:
                question = content
            break

    if x_session_id and question:
        cached = search_cache(x_session_id, question)
        if cached:
            cache_hits_total.inc()
            return {"content": [{"type": "text", "text": cached}]}

    try:
        cache_misses_total.inc()
        start = time.time()
        response = client.messages.create(
            model=request.model,
            max_tokens=request.max_tokens,
            system=request.system or "you are a helpful assistant.",
            messages=request.messages
        )
        answer = response.content[0].text
        llm_duration_seconds.observe(time.time() - start)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LLM call failed: {e}")

    if x_session_id and question:
        store_in_cache(x_session_id, question, answer)

    return {"content": [{"type": "text", "text": answer}]}    
  
    