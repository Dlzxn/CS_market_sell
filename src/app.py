from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from src.model.DataModel import DataModel, UpdateTimeData

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Разрешаем все методы, включая OPTIONS
    allow_headers=["*"], # Разрешаем все заголовки
)
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/get_api")
async def get_api(data: DataModel):
    return {
        "status": True,
        "user_id": "3922239393"
    }

@app.post("/updates_time")
async def update_time(data: UpdateTimeData):
    return {"status": True}