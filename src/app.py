from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from src.model.DataModel import DataModel, UpdateTimeData
from src.Routers.user_rout import user_rout

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_rout)

@app.get("/")
async def root():
    return {"message": "Hello"}
