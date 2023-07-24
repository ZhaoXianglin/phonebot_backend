from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from router import api, que, chat
import asyncio
import logging

import aioredis

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.api)
app.include_router(que.que)
app.include_router(chat.chat)


def register_redis(app: FastAPI):
    @app.on_event("startup")
    async def startup_event():
        app.state.redis = await aioredis.from_url("redis://redis-19591.c299.asia-northeast1-1.gce.cloud.redislabs.com",
                                                  port=19591,
                                                  password="19EyREFPXcF3DQcbXa6lF5KSvW6kIKF2",
                                                  encoding="utf-8", decode_responses=True)
        print(f"redis成功--->>{app.state.redis}")

    @app.on_event("shutdown")
    async def shutdown_event():
        await app.state.redis.close()


register_redis(app)


@app.get("/")
async def index():
    import numpy as np
    print(np.arange(3, 35, 3))
    return {"message": "Hello World!"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    handler = logging.handlers.RotatingFileHandler("api.log", mode="a", maxBytes=100 * 1024, backupCount=3)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
