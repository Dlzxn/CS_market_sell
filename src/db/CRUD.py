import json
from src.service.logger_cfg.log import logger
from src.model.DataModel import DataModel, UpdateTimeData
from typing import Any


class UserBD:
    """
    Пример db:
    json = {
        "users":
            [
                {
                    "user_id": 1,
                    "api_key": "3R2552fe4fDff424",
                    "time": 30,
                    "skins":[
                        {
                            "id": 1,
                            "currently_price": 233.45,
                            "min_price": 230,
                            "auto_reprice": True,
                        }
                    ]
                },
                {
                    "user_id": 2,
                    "api_key": "343TTR4353AFW3FA56FA4FW",
                    "time": 30,
                    "skins":[
                        {
                            "id": 542,
                            "currently_price": 276.85,
                            "min_price": 230,
                            "auto_reprice": True,
                        }
                    ]
                },
            ]
    }
    """
    def __init__(self) -> None:
        self.base = self.__load()

    @staticmethod
    def __load() -> tuple:
        with open("data/users.json", "r") as f:
            return json.load(f)

    def _dump(self) -> bool:
        with open("data/users.json", "w") as f:
            json.dump(self.base, f, indent=4)
            return True

    def create_user(self, user: DataModel) -> (bool, str):
        try:
            for x in self.base["users"]:
                if x["api_key"] == user.api_key:
                    user = x
                    return True, user["user_id"]
            if len(self.base["users"]) == 0:
                count = 0
            else:
                count = len(self.base["users"])

            user = {
                "user_id": count,
                "api_key": user.api_key,
                "time": 30,
                "skins": []
            }

            self.base["users"].append(user)
            if self._dump():
                logger.info("Base dumped with created user")
                return True, count
            else:
                return False, 0

        except KeyError:
            logger.error("KeyError | create_user function")

        except FileNotFoundError:
            logger.error("FileNotFound | create_user function")

        except Exception as e:
            logger.error(e)

        return False, 0

    def update_time(self, user: UpdateTimeData) -> bool:
        try:
            for x in self.base["users"]:
                if x["user_id"] == user.user_id:
                    x["time"] = user.check_interval
                    self._dump()
                    logger.info("User updated time | update_time function")
                    return True
            return False

        except KeyError:
            logger.error("KeyError | update_time function")

        except Exception as e:
            logger.error(e)





user_database = UserBD()
