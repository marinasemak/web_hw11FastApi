from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    database_test_url: str = "database_test_url"
    secret_key: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    redis_host: str = 'localhost'
    redis_port: int = 6379

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
