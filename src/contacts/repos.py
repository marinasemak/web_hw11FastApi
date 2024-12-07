from typing import List

from sqlalchemy import and_, extract, func, or_, select
from sqlalchemy.exc import IntegrityError

from src.contacts.models import Contact
from src.contacts.schema import ContactCreate, ContactUpdate


class ContactRepository:
    def __init__(self, session):
        self.session = session

    async def create_contact(self, contact: ContactCreate, owner_id: int) -> Contact:
        """
        Create new contact
        :param contact: Contact to create
        :type contact: ContactCreate
        :param owner_id: User who creates contact
        :type owner_id: int
        :return: Created contact
        :rtype: Contact
        """
        new_contact = Contact(**contact.model_dump(), owner_id=owner_id)
        try:
            self.session.add(new_contact)
            await self.session.commit()
            await self.session.refresh(new_contact)
            return new_contact
        except IntegrityError as e:
            raise Exception(str(e.orig))

    async def get_contact(self, owner_id: int, contact_id: int) -> Contact | None:
        """
        Get contact by id
        :param owner_id: User who created contact
        :type owner_id: int
        :param contact_id: Contact id
        :type contact_id: int
        :return: Contact from query
        :rtype: Contact | None
        """
        query = select(Contact).where(
            and_(Contact.owner_id == owner_id), (Contact.id == contact_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_contacts(
        self, owner_id: int, offset: int, limit: int
    ) -> List[Contact]:
        """
        Get list of contacts
        :param owner_id: User who created contacts
        :type owner_id: int
        :param offset: The number of contacts to skip
        :type offset: int
        :param limit: The max number of contacts to return
        :type limit: int
        :return: Contacts from query
        :rtype: List[Contact]
        """
        query = (
            select(Contact)
            .where(Contact.owner_id == owner_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def search_contacts(self, owner_id, param: str) -> List[Contact]:
        """
        Search contacts by first name or last name or email
        :param owner_id: User who created contacts
        :type owner_id: int
        :param param: First name or last name or email to search by
        :type param: str
        :return: Contacts from query
        :rtype: List[Contact]
        """
        query = (
            select(Contact)
            .where(Contact.owner_id == owner_id)
            .filter(
                or_(
                    Contact.first_name == param,
                    Contact.last_name == param,
                    Contact.email == param,
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_contact(
        self, owner_id, contact_id: int, new_contact: ContactUpdate
    ) -> Contact | None:
        """
        Update contact
        :param owner_id: User who created contact
        :type owner_id: int
        :param contact_id: Id of contact to update
        :type contact_id: str
        :param new_contact: Contact data to update
        :type contact_id: ContactUpdate
        :return: Updated contact
        :rtype: Contact | None
        """
        query = select(Contact).where(
            and_(Contact.owner_id == owner_id), (Contact.id == contact_id)
        )
        contact = await self.session.execute(query)
        contact = contact.scalar_one_or_none()
        if contact:
            update_data = new_contact.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(contact, key, value)
            try:
                await self.session.commit()
                await self.session.refresh(contact)
                return contact
            except IntegrityError as e:
                raise Exception(str(e.orig))

    async def remove_contact(self, owner_id, contact_id: int) -> Contact | None:
        """
        Remove contact
        :param owner_id: User who created contact
        :type owner_id: int
        :param contact_id: Id of contact to remove
        :type contact_id: str
        :return: Removed contact
        :rtype: Contact | None
        """
        query = select(Contact).where(
            and_(Contact.owner_id == owner_id), (Contact.id == contact_id)
        )
        contact = await self.session.execute(query)
        contact = contact.scalar_one_or_none()
        if contact:
            await self.session.delete(contact)
            await self.session.commit()
            return contact

    async def get_upcoming_birthdays(self, owner_id) -> List[Contact]:
        """
        Selects list of contacts who's upcoming birthdays within 7 days
        :param owner_id: User who created contacts
        :type owner_id: int
        :return: List of contacts
        :rtype: List[Contact]
        """
        query = (
            select(Contact)
            .where(Contact.owner_id == owner_id)
            .filter(
                or_(
                    (
                        func.mod(
                            extract("doy", func.current_date())
                            - extract("doy", Contact.birthday)
                            + 365,
                            365,
                        )
                        <= 7
                    ),
                    (
                        func.mod(
                            extract("doy", Contact.birthday)
                            - extract("doy", func.current_date())
                            + 365,
                            365,
                        )
                        <= 7
                    ),
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()
