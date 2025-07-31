from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Bot settings
    BOT_TOKEN: str
    WEBHOOK_URL: str
    WEBHOOK_PATH: str = "/webhook"
    WEBHOOK_SECRET: str = "my-secret"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./converter_bot.db"
    
    # File settings
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    TEMP_DIR: str = "./temp"
    
    # AI Services (optional)
    OPENAI_API_KEY: Optional[str] = None
    
    # Admin
    ADMIN_IDS: list[int] = []
    
    class Config:
        env_file = ".env"

settings = Settings()