import asyncio
import uvicorn
from fastapi import FastAPI

from app.config import config
from app.presentation.api import router
from app.bot.start_bot import start_bot

app = FastAPI()
app.include_router(router)


async def main() -> None:
    server_config = uvicorn.Config(
        app, host="0.0.0.0", port=config.API_PORT, loop="asyncio", reload=False
    )
    server = uvicorn.Server(server_config)

    bot_task = asyncio.create_task(start_bot())
    api_task = asyncio.create_task(server.serve())

    await asyncio.gather(bot_task, api_task)


if __name__ == "__main__":
    asyncio.run(main())
