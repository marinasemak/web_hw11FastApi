from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_db
from src.auth.models import User
from src.auth.utils import get_current_user
from src.contacts.repos import ContactRepository
from src.contacts.schema import Contact, ContactCreate, ContactResponse, ContactUpdate

router = APIRouter()


async def unexpected_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={f"message": "An unexpected error occurred"},
    )


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    description="No more than 5 requests per minute",
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def create_contact(
    contact: ContactCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Contact:
    """
    Request to create new contact
    :param contact: Contact to create
    :type contact: ContactCreate
    :param user: The user to create contacts for
    :type user: User
    :param db: The database session
    :type db: Session
    :return: Created contact
    :rtype: ContactResponse
    """
    contact_repo = ContactRepository(db)
    try:
        return await contact_repo.create_contact(contact, user.id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get(
    "/",
    response_model=List[ContactResponse],
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_contacts(
    offset: int = 0,
    limit: int = Query(default=10, le=100, ge=10),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Request to get list of contacts with specified offset and limit
    :param offset: The number of contacts to skip
    :type offset: int
    :param limit: The max number of contacts to return
    :type limit: int
    :param user: The user to get contacts for
    :type user: User
    :param db: The database session
    :type db: Session
    :return: List of contacts
    :rtype: List[ContactResponse]
    """
    contact_repo = ContactRepository(db)
    contacts = await contact_repo.get_contacts(user.id, offset, limit)
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found"
        )
    return contacts


@router.get(
    "/search",
    response_model=ContactResponse,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def search_contact(
    param: str = Query(description="Search by first name or last name or email"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Search contacts by first name or last name or email
    :param param: First name or last name or email to search by
    :type param: str
    :param user: User who created contacts
    :type user: User
    :param db: The database session
    :type db: Session
    :return: Searched contact
    :rtype: ContactResponse
    """
    contact_repo = ContactRepository(db)
    contact = await contact_repo.search_contacts(user.id, param)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found"
        )
    return contact


@router.get(
    "/upcomingBirthdays",
    response_model=List[ContactResponse],
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_upcoming_birthdays(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Gives the list of contacts with upcoming birthdays within the next 7 days
    :param user: User who created contacts
    :type user: User
    :param db: The database session
    :type db: Session
    :return: List of contacts
    :rtype: List[ContactResponse]
    """
    contact_repo = ContactRepository(db)
    contact = await contact_repo.get_upcoming_birthdays(user.id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found"
        )
    return contact


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_contact(
    contact_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Contact:
    """
    Get contact by id
    :param contact_id: Contact id
    :type contact_id: int
    :param user: User who created contact
    :type user: User
    :param db: The database session
    :type db: Session
    :return: Contact from query
    :rtype: Contact | None
    """
    contact_repo = ContactRepository(db)
    contact = await contact_repo.get_contact(user.id, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.put(
    "/{contact_id}",
    response_model=ContactResponse,
    description="No more than 5 requests per minute",
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def update_contact(
    contact_id: int,
    contact: ContactUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Contact:
    """
    Update contact
    :param contact_id: Id of contact to update
    :type contact_id: int
    :param contact: Contact data to update
    :type contact: ContactUpdate
    :param user: User who created contact
    :type user: int
    :param db: The database session
    :type db: Session
    :return: Updated contact
    :rtype: ContactResponse | None
    """
    contact_repo = ContactRepository(db)
    try:
        contact = await contact_repo.update_contact(user.id, contact_id, contact)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
            )
        return contact
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete(
    "/{contact_id}",
    response_model=ContactResponse,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def delete_contact(
    contact_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove contact
    :param contact_id: Id of contact to remove
    :type contact_id: int
    :param user: User who created contact
    :type user: int
    :param db: The database session
    :type db: Session
    :return: Removed contact
    :rtype: ContactResponse | None
    """
    contact_repo = ContactRepository(db)
    contact = await contact_repo.remove_contact(user.id, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
