# CacheIt

A semantic caching proxy layer for LLM APIs. Sits in front of any Anthropic-compatible endpoint, detects semantically similar queries using vector embeddings, and serves cached responses instantly — reducing API costs and latency without changing your application code.

---

## The Problem

Every time a user asks "What is recursion?" and another asks "Can you explain recursion to me?", your app makes two identical LLM API calls. At scale, this adds up fast — redundant calls, redundant costs, redundant latency.

CacheIt intercepts these calls, embeds the incoming question, and checks if a semantically similar question has been answered before. If yes, it returns the cached answer in milliseconds. If no, it forwards the request to the real LLM, caches the response, and returns it.

---

## How It Works

```
Incoming question
        ↓
Embed with BAAI/bge-small-en-v1.5 (local, free)
        ↓
Search Redis vector index for nearest neighbor
        ↓
Similarity > 0.90?
   YES → return cached answer instantly (~2ms)
   NO  → call Anthropic API, cache response, return answer
```

Each user session gets its own isolated Redis index — answers from one session never bleed into another, even if users ask identical questions against different documents.

---

## Tech Stack

| Component | Tool |
|---|---|
| Proxy layer | FastAPI |
| Embeddings | BAAI/bge-small-en-v1.5 (local, HuggingFace) |
| Vector store | Redis Stack + RediSearch (HNSW index) |
| LLM | Anthropic Claude (claude-haiku-4-5) |
| Containerization | Docker + docker-compose |
| Persistence | Redis AOF (Append Only File) |

---

## Performance (Prometheus-validated, 30-request load test)

| Metric | Value |
|---|---|
| Hit rate | 60% |
| Avg latency — cache hit | ~127ms |
| Avg latency — cache miss | 3.61s |
| P95 latency — cache miss | 6s |
| Latency reduction on hit | ~96% |

*Queries validated via Prometheus. Load test: 10 unique questions × 3 rounds (miss, hit, paraphrase).*

## Threshold Validation

The 0.90 similarity threshold wasn't chosen arbitrarily — it was validated against the STS (Semantic Textual Similarity) benchmark using the same embedding model used in production.

| Group | Avg Cosine Similarity |
|---|---|
| Same meaning pairs (human score ≥ 0.8) | 0.9113 |
| Different meaning pairs (human score < 0.8) | 0.8070 |
| Suggested threshold (midpoint) | 0.8592 |
| **Chosen threshold** | **0.90** |

The threshold is set at 0.90 — above the midpoint and closer to the "same meaning" cluster — to prioritize precision over recall. A false cache hit (serving a wrong cached answer) is worse than a false miss (an extra LLM call).

---

## API Endpoints

### Session Management

```
POST   /session/{session_id}   — Create a new cache index for a session
DELETE /session/{session_id}   — Delete session cache when session ends
```

### Proxy

```
POST /v1/messages
```

Request body:
```json
{
  "session_id": "abc123",
  "question": "What is recursion?",
  "messages": [{"role": "user", "content": "What is recursion?"}],
  "system": "You are a helpful assistant."
}
```

Response:
```json
{
  "answer": "Recursion is...",
  "cache_hit": true
}
```

The `cache_hit` field tells you whether the response was served from cache or from the LLM — useful for monitoring and analytics.

### Health Check

```
GET /health   — Returns {"status": "ok"}
```

---

## Running Locally

**Prerequisites:** Docker Desktop

```bash
git clone https://github.com/yourusername/cacheit.git
cd cacheit

# Add your Anthropic API key
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY

# Start everything
docker compose up --build
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- RedisInsight: http://localhost:8001

---

## Integration

Point any app at CacheIt instead of Anthropic by changing one line.

**LlamaIndex (Parsit integration):**
```python
from llama_index.llms.anthropic import Anthropic

llm = Anthropic(
    model="claude-haiku-4-5",
    api_key=ANTHROPIC_API_KEY,
    base_url="http://cacheit:8000"  # ← this one line
)
```

Any app calling the Anthropic API can integrate with CacheIt by pointing its base URL at the proxy.

---

## Integration with Parsit

CacheIt is integrated with [Parsit](https://github.com/twin/parsit), a full stack RAG app that lets you chat with your own documents.

**How it works:**
- When a Parsit session starts, it calls `POST /session/{session_id}` to create an isolated cache index in Redis
- Every chat request goes through CacheIt before reaching Claude
- On a cache hit, the answer is returned instantly — no LLM call, no document retrieval
- When the session ends, Parsit calls `DELETE /session/{session_id}` to clean up

**Integration change in Parsit — one line:**
```python
llm = Anthropic(
    model="claude-haiku-4-5",
    api_key=ANTHROPIC_API_KEY,
    base_url="http://cacheit:8000"  # ← this one line
)
```


## Project Context

CacheIt is part of a two-phase AI engineering portfolio:

1. **CacheIt** (this project) — standalone semantic cache proxy
2. **Parsit + CacheIt** — integrating the cache in front of a RAG app to show real cost/latency reduction with numbers


---

## Built By

Jaya Sankar Sailesh — AI/Software Engineer  