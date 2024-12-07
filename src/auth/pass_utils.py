from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, password_hashed: str) -> bool:
    """
    Verify if user enters password the same as its hashed version in db
    :param plain_password: User password.
    :type plain_password: str
    :param password_hashed: Hashed user password
    :type password_hashed: str
    :return: If password is valid
    :rtype: bool
    """
    return pwd_context.verify(plain_password, password_hashed)


def get_password_hash(password: str) -> str:
    """
    Hash user password
    :param password: User password in hashed view.
    :type password: str
    :return: Hashed password
    :rtype: str
    """
    return pwd_context.hash(password)
