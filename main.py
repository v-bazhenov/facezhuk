import redis.asyncio as redis
import uvicorn
from fastapi import APIRouter, WebSocket
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi_limiter import FastAPILimiter
from fastapi_pagination import add_pagination
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.websockets import WebSocketDisconnect

from auth.api import auth_router
from chat.api import chat_router
from common.exceptions import HTTPExceptionJSON
from config import cfg
from database.core import db
from notification.api import notification_router
from notification.manager import notifier
from profile.api import profiles_router

# Init FastAPI app
app = FastAPI(debug=cfg.debug)

# CORS
if not cfg.debug:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add routers
api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router, tags=["Auth"])
api_router.include_router(profiles_router, tags=["Profiles"])
api_router.include_router(notification_router, tags=["Notifications"])
api_router.include_router(chat_router, tags=["Chat"])
app.include_router(api_router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await notifier.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        notifier.remove(websocket)


# Add exception handlers
@app.exception_handler(HTTPExceptionJSON)
async def http_exception_handler(
        request: Request,
        exc: HTTPExceptionJSON):
    json_data = jsonable_encoder(exc.data)
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={"message": exc.detail, "code": exc.code, "error": json_data})


# Startup event handler
@app.on_event("startup")
async def startup():
    # Connect FastAPILimiter
    _redis = redis.from_url(cfg.cache_uri, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(_redis)
    # Connect to database
    await db.connect()
    # Connect to MongoDB
    app.mongodb_client = AsyncIOMotorClient(cfg.mongo_db_uri)
    app.mongodb = app.mongodb_client[cfg.mongo_db_name]


# Shutdown event handler
@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()
    app.mongodb_client.close()

add_pagination(app)

if __name__ == "__main__":
    uvicorn.run("main:app", log_level=cfg.fastapi_log_level, reload=True)
