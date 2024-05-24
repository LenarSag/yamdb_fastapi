import asyncio

import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import ValidationException

from db.database import init_models
from api.login import loginroute
from api.users import usersrouter
from api.categories import categoryrouter
from api.genres import genresrouter
from api.titles import titlesrouter


app = FastAPI()

app.include_router(loginroute, prefix="/auth")
app.include_router(usersrouter, prefix="/users")
app.include_router(categoryrouter, prefix="/categories")
app.include_router(genresrouter, prefix="/genres")
app.include_router(titlesrouter, prefix="/titles")


@app.exception_handler(ValidationException)
async def custom_pydantic_validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.errors()}
    )


@app.get("/")
async def index():
    return "Blogicum Fastapi"


if __name__ == "__main__":
    asyncio.run(init_models())
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
