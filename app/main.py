from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import proxy
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator



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



@app.get("/health")
def health():
    return {"status": "ok"}