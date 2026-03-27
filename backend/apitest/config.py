from pydantic_settings import BaseSettings
from urllib.parse import quote_plus

class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "Test@123456"
    DB_NAME: str = "test_platform"
    
    class Config:
        env_file = ".env"
    
    @property
    def database_url(self) -> str:
        # URL编码密码，避免特殊字符导致解析错误
        password = quote_plus(self.DB_PASSWORD)
        return f"mysql+pymysql://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()

