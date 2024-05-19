import asyncio

import uvicorn
from fastapi import FastAPI

from db.database import init_models
from api.login import loginroute


app = FastAPI()

app.include_router(loginroute, prefix="/auth")


@app.get("/")
async def index():
    return "Blogicum Fastapi"


if __name__ == "__main__":
    asyncio.run(init_models())
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
