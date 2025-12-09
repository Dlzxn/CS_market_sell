import json, os
from src.service.logger_cfg.log import logger
from src.model.DataModel import DataModel, UpdateTimeData, SkinSettings
from typing import Any
from filelock import FileLock


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
        self.base = None
        self.__load()

    def __load(self) -> bool:
        lock = FileLock("data/users.json.lock")
        with lock:
            if not os.path.exists("data/users.json"):
                return False
            with open("data/users.json", "r") as f:
                self.base = json.load(f)
                return True

    def _dump(self) -> bool:
        lock = FileLock("data/users.json.lock")
        with lock:
            with open("data/users.json", "w") as f:
                json.dump(self.base, f, indent=4)
                return True

    def delete_skin(self, user_id: int, skin_id: int) -> bool:
        self.__load()
        try:
            for x in self.base["users"]:
                if x["user_id"] == user_id:
                    for skin in x["skins"]:
                        if skin["id"] == skin_id:
                            x["skins"].remove(skin)
                            self._dump()
                            logger.info(f"Скин с айди f{skin_id} был удален с базы данных")
                            break
            logger.info(f"У пользователя с id {user_id} не нашлось скинов на удаление")
            return True
        except Exception as e:
            logger.error(f"При удалении скинов произошла ошибка | {e}")
            return False


    def create_user(self, user: DataModel) -> (bool, str):
        self.__load()
        try:
            for x in self.base["users"]:
                if x["api_key"] == user.api_key:
                    user = x
                    return True, user["user_id"]

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
            return False, 0

        except FileNotFoundError:
            logger.error("FileNotFound | create_user function")
            return False, 0

        except Exception as e:
            logger.error(e)
            return False, 0


    def update_time(self, user: UpdateTimeData) -> bool:
        self.__load()
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
            return False

        except Exception as e:
            logger.error(e)
            return False

    def update_skin(self, data: SkinSettings) -> bool:
        self.__load()
        try:
            flag = False
            for x in self.base["users"]:
                if x["user_id"] == data.user_id:
                    user = x
                    flag = True
            if not flag:
                return False
            flag = False
            for x in user["skins"]:
                if x["id"] == data.skin_id:
                    flag = True
                    x["min_price"] = data.min
                    x["auto_reprice"] = data.enabled
                    self._dump()
                    logger.info("User updated skins | update_skins function")
                    return True
            if flag == False:
                skin = {
                            "id": data.skin_id,
                            "currently_price": None,
                            "min_price": data.min,
                            "auto_reprice": data.enabled,
                        }
                user["skins"].append(skin)
                self._dump()
                logger.info("User updated skins | update_skins function")
                return True

            return False

        except KeyError:
            logger.error("KeyError | update_skins function")
            return False

        except Exception as e:
            logger.error(e)
            return False

    def get_info_by_id(self, id: int) -> dict | None:
        self.__load()
        for x in self.base["users"]:
            if x["user_id"] == id:
                return x
        return None

    def get_all_id(self) -> list:
        self.__load()
        sp = []
        for x in self.base["users"]:
            sp.append((x["user_id"], x["time"]))
        return sp



user_database = UserBD()
