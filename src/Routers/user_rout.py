from fastapi import APIRouter

from src.db.CRUD import user_database
from src.model.DataModel import DataModel, UpdateTimeData

user_rout = APIRouter(prefix="/users")

@user_rout.post("/get_api")
async def get_api(data: DataModel):
    is_created, id = user_database.create_user(data)

    if is_created:
        return {
            "status": True,
            "user_id": id
        }
    else:
        return {
            "status": False,
            "user_id": "ERROR"
        }

@user_rout.post("/updates_time")
async def update_time(data: UpdateTimeData):
    status = user_database.update_time(data)
    return {"status": status}