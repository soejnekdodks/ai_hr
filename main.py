import asyncio
import uvicorn
from fastapi import FastAPI

from app.config import config
from app.presentation.api import router
from app.bot.start_bot import start_bot

# app = FastAPI()
# app.include_router(router)

if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=config.API_PORT)
    asyncio.run(start_bot())
