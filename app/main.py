from fastapi import FastAPI
from .routers import health, agents

app = FastAPI(title="Fortior Agency AI — platform")
app.include_router(health.router)
app.include_router(agents.router)
