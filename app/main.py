from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import proxy
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram


@asynccontextmanager
async def lifespan(app: FastAPI):
    instrumentator.expose(app)
    yield

app = FastAPI(lifespan=lifespan)

instrumentator = Instrumentator().instrument(app)

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(proxy.router)

cache_hits_total = Counter("cacheit_hits_total", "Total cache hits")
cache_misses_total = Counter("cacheit_misses_total", "Total cache misses")
llm_duration_seconds = Histogram("caceit_llm_duration_seconds", "LLM call duration in seconds")

@app.get("/health")
def health():
    return {"status": "ok"}