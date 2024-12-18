from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
)
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary
import cloudinary.uploader

from config.db import get_db
from config.general import settings
from src.auth.models import User
from src.auth.repos import UserRepository
from src.auth.schema import UserResponse
from src.auth.utils import get_current_user


router = APIRouter()


@router.get("/my-account", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Request to show account of current user
    :param current_user: The user who makes request
    :type current_user: User
    :param db: The database session
    :type db: Session
    :return: Current user info
    :rtype: UserResponse
    """
    return current_user


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar(
    file: UploadFile = File(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Request to update avatar of current user
    :param file: Image file to upload
    :type file: UploadFile
    :param current_user: Current user to update avatar for
    :type current_user: User
    :param db: The database session
    :type db: Session
    :return: User info with updated avatar link from db
    :rtype: UserResponse
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

    r = cloudinary.uploader.upload(
        file.file, public_id=f"ContactsApp/{current_user.username}", overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(
        f"ContactsApp/{current_user.username}"
    ).build_url(width=250, height=250, crop="fill", version=r.get("version"))
    user_repo = UserRepository(db)
    user = await user_repo.update_avatar(current_user.email, src_url)
    return user
