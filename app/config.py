
from pathlib import Path
from urllib.parse import quote

from pydantic_settings import BaseSettings, SettingsConfigDict

# 获取项目根目录（python-backend 目录）
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):

    server_port: int = 8567
    server_host: str = "0.0.0.0"

    db_host: str
    db_port: int = 3306
    db_name: str
    db_user: str
    db_password: str

    redis_host: str
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    session_secret_key: str
    session_max_age: int = 2592000  # 30 天

    password_salt: str

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def database_url(self) -> str:
        """获取数据库连接 URL"""
        return f"mysql+pymysql://{self.db_user}:{quote(self.db_password)}@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"

    @property
    def redis_url(self) -> str:
        """获取 Redis 连接 URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()

if __name__ == "__main__":
    settings.db_password = quote(settings.db_password)
    print(settings.db_password)
    print(settings.database_url)
    print(settings.redis_url)
