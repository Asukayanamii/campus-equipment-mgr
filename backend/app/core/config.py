import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# 当前文件：backend/app/core/config.py
current_file_dir = os.path.dirname(__file__)
# 向上两级：backend/
backend_root = os.path.join(current_file_dir, "..", "..")
# 拼接 backend/.env 绝对路径
env_file_abs = os.path.join(backend_root, ".env")

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE: str

    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

    model_config = SettingsConfigDict(
        env_file=env_file_abs,
        env_file_encoding="utf-8"
    )

settings = Settings()