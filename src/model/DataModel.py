from pydantic import BaseModel

class DataModel(BaseModel):
    api_key: str | int

class UpdateTimeData(BaseModel):
    user_id: str | int
    check_interval: int | str