from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from router import api
import asyncio

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


def register_redis(app: FastAPI):
    @app.on_event("startup")
    async def startup_event():
        app.state.redis = await aioredis.from_url("redis://redis-10499.c54.ap-northeast-1-2.ec2.cloud.redislabs.com",
                                                  port=10499,
                                                  password="KmIe8HC79I20Q0dvZb58dL1VKbYHTVZQ",
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
