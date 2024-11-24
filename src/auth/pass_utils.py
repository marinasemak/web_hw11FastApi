from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, password_hashed):
    return pwd_context.verify(plain_password, password_hashed)


def get_password_hash(password):
    return pwd_context.hash(password)
