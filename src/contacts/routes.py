from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_db
from src.contacts.repos import ContactRepository
from src.contacts.schema import Contact, ContactCreate, ContactResponse, ContactUpdate

router = APIRouter()


async def unexpected_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={f"message": "An unexpected error occurred"},
    )


@router.post("/", response_model=ContactResponse)
async def create_contact(
    contact: ContactCreate, db: AsyncSession = Depends(get_db)
) -> Contact:
    contact_repo = ContactRepository(db)
    try:
        new_contact = await contact_repo.create_contact(contact)
        return new_contact
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    offset: int = 0,
    limit: int = Query(default=10, le=100, ge=10),
    db: AsyncSession = Depends(get_db),
):
    contact_repo = ContactRepository(db)
    contacts = await contact_repo.get_contacts(offset, limit)
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found"
        )
    return contacts


@router.get("/search", response_model=ContactResponse)
async def search_contact(
    param: str = Query(description="Search by first name or last name or email"),
    db: AsyncSession = Depends(get_db),
):
    contact_repo = ContactRepository(db)
    contact = await contact_repo.search_contacts(param)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found"
        )
    return contact


@router.get("/upcomingBirthdays", response_model=List[ContactResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    """
    Gives the list of contacts with upcoming birthdays within the next 7 days
    """
    contact_repo = ContactRepository(db)
    contact = await contact_repo.get_upcoming_birthdays()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found"
        )
    return contact


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)) -> Contact:
    contact_repo = ContactRepository(db)
    contact = await contact_repo.get_contact(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int, contact: ContactUpdate, db: AsyncSession = Depends(get_db)
) -> Contact:
    contact_repo = ContactRepository(db)
    try:
        contact = await contact_repo.update_contact(contact_id, contact)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
            )
        return contact
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact_repo = ContactRepository(db)
    contact = await contact_repo.remove_contact(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
