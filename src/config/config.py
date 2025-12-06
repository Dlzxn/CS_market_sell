from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


__all__ = ('Config', )


class Config(BaseSettings):
    api_key: SecretStr

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
        )