from fastapi import FastAPI
from .routers import health
app = FastAPI(title="multinicho-platform")
app.include_router(health.router)
