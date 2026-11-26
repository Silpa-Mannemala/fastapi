from fastapi import FastAPI

from app.routes.devices import router

app = FastAPI(title="Device API")
app.include_router(router)
