from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):

    supabase_url: str
    supabase_key: str


    admin_username: str = "admin"
    admin_password: str = "admin123"
    secret_key: str = "your-secret-key-here-change-in-production"
    debug: bool = False


    app_title: str = "Панель управления ИИ-агентом обучения"
    app_description: str = "Админ-панель для управления телеграм ботом обучения"
    app_version: str = "1.0.0"


    page_size: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()