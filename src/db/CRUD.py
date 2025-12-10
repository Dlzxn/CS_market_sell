from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from src.service.logger_cfg.log import logger
from src.model.DataModel import DataModel, UpdateTimeData, SkinSettings
from typing import Any, List, Tuple, Dict
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "cs_market_db"
COLLECTION_NAME = "users"


class UserBD:
    def __init__(self) -> None:
        try:
            print("Попытка подключения....")
            self.client = MongoClient(MONGO_URI)
            self.db = self.client[DATABASE_NAME]
            self.collection = self.db[COLLECTION_NAME]

            self.collection.create_index("user_id", unique=True)
            self.collection.create_index("api_key", unique=True)
            logger.info("Успешное подключение к MongoDB.")

        except ConnectionError as e:
            logger.error(f"Ошибка подключения к MongoDB: {e}")
            raise ConnectionError("Не удалось подключиться к базе данных MongoDB.")
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при инициализации БД: {e}")
            raise

    def delete_skin(self, user_id: int, skin_id: int) -> bool:
        try:
            result = self.collection.update_one(
                {"user_id": user_id},
                {"$pull": {"skins": {"id": skin_id}}}
            )

            if result.modified_count > 0:
                logger.info(f"Скин с ID {skin_id} был удален из базы данных у пользователя {user_id}.")
                return True
            else:
                logger.info(f"Скин с ID {skin_id} не найден для удаления у пользователя {user_id}.")
                return False
        except Exception as e:
            logger.error(f"При удалении скинов произошла ошибка | {e}")
            return False

    def create_user(self, user_data: DataModel) -> Tuple[bool, int]:
        try:
            existing_user = self.collection.find_one({"api_key": user_data.api_key})
            if existing_user:
                return True, existing_user["user_id"]

            last_user = self.collection.find_one(sort=[("user_id", -1)])
            new_user_id = (last_user["user_id"] + 1) if last_user else 0

            new_document = {
                "user_id": new_user_id,
                "api_key": user_data.api_key,
                "time": 30,
                "skins": []
            }

            self.collection.insert_one(new_document)
            logger.info(f"Новый пользователь создан с ID: {new_user_id}")
            return True, new_user_id

        except DuplicateKeyError:
            logger.error("Ошибка DuplicateKeyError при создании пользователя.")
            return False, 0
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя | {e}")
            return False, 0

    def update_time(self, user_data: UpdateTimeData) -> bool:
        try:
            result = self.collection.update_one(
                {"user_id": user_data.user_id},
                {"$set": {"time": user_data.check_interval}}
            )
            if result.modified_count > 0:
                logger.info(f"User {user_data.user_id} updated time.")
                return True
            return False

        except Exception as e:
            logger.error(f"Ошибка обновления времени | {e}")
            return False

    def update_skin(self, data: SkinSettings) -> bool:
        try:
            result = self.collection.update_one(
                {"user_id": data.user_id, "skins.id": data.skin_id},
                {"$set": {
                    "skins.$.min_price": data.min,
                    "skins.$.auto_reprice": data.enabled
                }}
            )

            if int(result.modified_count) > 0:
                logger.info(f"Скин {data.skin_id} обновлен у пользователя {data.user_id}.")
                return True

            if int(result.matched_count) == 0:
                new_skin = {
                    "id": data.skin_id,
                    "currently_price": None,
                    "min_price": data.min,
                    "auto_reprice": data.enabled,
                }

                result = self.collection.update_one(
                    {"user_id": data.user_id},
                    {"$push": {"skins": new_skin}}
                )

                if int(result.modified_count) > 0:
                    logger.info(f"Скин {data.skin_id} добавлен к пользователю {data.user_id}.")
                    return True
                else:
                    logger.info("При выставлении скина ничего не поменялось стр 122")
                    return False
            logger.info(f"Скин уже есть в базе данных")
            return False

        except Exception as e:
            logger.error(f"Ошибка обновления/добавления скина: {e}")
            return False

    def get_info_by_id(self, user_id: int) -> Dict[str, Any] | None:
        user_document = self.collection.find_one({"user_id": user_id}, {"_id": 0})
        return user_document

    def get_all_id(self) -> List[Tuple[int, int]]:
        users_cursor = self.collection.find({}, {"_id": 0, "user_id": 1, "time": 1})

        results = []
        for user in users_cursor:
            results.append((user.get("user_id"), user.get("time")))

        return results


user_database = UserBD()