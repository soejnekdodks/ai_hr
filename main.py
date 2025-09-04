import uvicorn
from fastapi import FastAPI

from app.presentation.api import router
from app.config import config

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config.API_PORT)
