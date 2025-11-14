from pydantic_settings import BaseSettings
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    DATABASE_URL: str
    RABBITMQ_BROKER_URL: str
    REDIS_URL: str
    SENDGRID_API_KEY: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    FIREBASE_CREDENTIALS_PATH: str
    DEFAULT_FROM_EMAIL: str
    SECRET_KEY: str
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

logger.info("Configuration settings loaded successfully.")