from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from router import api

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.api)


@app.get("/")
async def index():
    import numpy as np
    print(np.arange(3, 35, 3))
    return {"message": "Hello World!"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
