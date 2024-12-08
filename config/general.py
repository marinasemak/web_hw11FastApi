from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_TEST_URL = os.getenv("DATABASE_TEST_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_SERVER = os.getenv("MAIL_SERVER")
CLOUDINARY_NAME = os.getenv("CLOUDINARY_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")


class Settings(BaseSettings):
    database_url: str = DATABASE_URL
    database_test_url: str = DATABASE_TEST_URL
    secret_key: str = SECRET_KEY
    mail_username: str = MAIL_USERNAME
    mail_password: str = MAIL_PASSWORD
    mail_from: str = MAIL_FROM
    mail_port: int = MAIL_PORT
    mail_server: str = MAIL_SERVER
    cloudinary_name: str = CLOUDINARY_NAME
    cloudinary_api_key: str = CLOUDINARY_API_KEY
    cloudinary_api_secret: str = CLOUDINARY_API_SECRET
    redis_host: str = REDIS_HOST
    redis_port: int = REDIS_PORT

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
