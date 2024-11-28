from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
