from sqlalchemy import select
from libgravatar import Gravatar
from starlette.datastructures import URL

from src.auth.models import User
from src.auth.pass_utils import get_password_hash
from src.auth.schema import UserCreate


class UserRepository:
    def __init__(self, session):
        self.session = session

    async def create_user(self, user_create: UserCreate) -> User:
        """
            Creates new user in db

            :param user_create: The user to create.
            :type user_create: UserCreate
            :return: Created user
            :rtype: User
        """
        avatar = None
        try:
            g = Gravatar(user_create.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)
        password_hashed = get_password_hash(user_create.password)
        new_user = User(
            username=user_create.username,
            email=user_create.email,
            password_hashed=password_hashed,
            avatar=avatar,
            is_active=False,
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)  # To get the ID from the db
        return new_user

    async def get_user_by_email(self, email: str) -> User | None:
        """
            Find user by email in db

            :param email: User email.
            :type email: str
            :return: User with specified email
            :rtype: User | None
        """
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def activate_user(self, user: User):
        """
            Activates created user

            :param user: The user to activate.
            :type user: User
        """
        user.is_active = True
        await self.session.commit()
        await self.session.refresh(user)

    async def update_avatar(self, email: str, url: URL) -> User:
        """
            Update user avatar
            :param email: User email.
            :type email: str
            :param url: Url with generated user avatar
            :type url: URL
            :return: User with updated avatar
            :rtype: User
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.session.commit()
        await self.session.refresh(user)
        return user
