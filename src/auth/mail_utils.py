from fastapi_mail import ConnectionConfig, MessageSchema, FastMail
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr, BaseModel
from jinja2 import Environment, FileSystemLoader
from starlette.datastructures import URL

from config.general import settings
from src.auth.utils import create_verification_token

env = Environment(loader=FileSystemLoader("src/templates"))


class EmailSchema(BaseModel):
    email: EmailStr


mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)


async def send_verification_email(email: EmailStr, host: URL):
    try:
        verification_token = create_verification_token(email)
        template = env.get_template("verification_email.html")
        email_body = template.render(host=host, token=verification_token)
        message = MessageSchema(
            subject="Email verification",
            recipients=[email],
            body=email_body,
            subtype="html",
        )

        fm = FastMail(mail_conf)
        await fm.send_message(message)
    except ConnectionErrors as err:
        print(err)
