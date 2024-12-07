import unittest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.orm import Session
from datetime import date

from src.contacts.models import Contact
from src.auth.models import User
from src.contacts.schema import Contact, ContactCreate, ContactResponse, ContactUpdate
from src.contacts.repos import ContactRepository


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = AsyncMock(spec=Session)
        self.test_instance = ContactRepository(self.session)
        self.user = User(id=1)
        self.contact = Contact(
            id=2,
            owner_id=1,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+380912223344",
            birthday=date(1990, 10, 12),
        )

    async def test_create_contact(self):
        new_contact = ContactCreate(
            owner_id=1,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+380912223344",
            birthday=date(1990, 10, 12),
        )
        # test_instance = ContactRepository(self.session)
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()

        result = await self.test_instance.create_contact(new_contact, self.user.id)
        self.assertEqual(result.first_name, self.contact.first_name)
        self.assertEqual(result.last_name, self.contact.last_name)
        self.assertEqual(result.email, self.contact.email)
        self.assertEqual(result.phone, self.contact.phone)
        self.assertEqual(result.birthday, self.contact.birthday)
        # self.assertEqual(result.owner_id, self.contact.owner_id)

    async def test_get_contact(self):
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = self.contact

        async def mock_execute(query):
            return mocked_result

        self.session.execute = mock_execute

        result = await self.test_instance.get_contact(self.user.id, contact_id=2)
        self.assertEqual(result, self.contact)

    async def test_get_contact_not_found(self):
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = None
        # self.session.execute.return_value = mocked_result

        async def mock_execute(query):
            return mocked_result

        self.session.execute = mock_execute

        result = await self.test_instance.get_contact(self.user.id, contact_id=2)
        self.assertIsNone(result)

    async def test_get_contacts(self):
        offset = 0
        limit = 10
        contacts = [Contact(
            id=1,
            owner_id=1,
            first_name="Tilda",
            last_name="Swinton",
            email="tilda.s@example.com",
            phone="+380923341122",
            birthday=date(1992, 12, 10),
        ), Contact(
            id=2,
            owner_id=1,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+380912223344",
            birthday=date(1990, 10, 12),
        )]
        mocked_result = MagicMock()
        mocked_result.scalars.return_value.all.return_value = contacts

        async def mock_execute(query):
            return mocked_result

        self.session.execute = mock_execute

        result = await self.test_instance.get_contacts(self.user.id, offset, limit)
        self.assertEqual(result, contacts)

    async def test_search_contact(self):
        param = "John"
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = self.contact

        async def mock_execute(query):
            return mocked_result

        self.session.execute = mock_execute

        result = await self.test_instance.search_contacts(self.user.id, param)
        self.assertEqual(result, self.contact)

    async def test_update_contact(self):
        contact_update = ContactUpdate(
            owner_id=1,
            first_name="Frank",
            last_name="Sinatra",
            email="frank.s@example.com",
            phone="+380912223344",
            birthday=date(1990, 10, 12),
        )
        contact = Contact(
            owner_id=1,
            first_name="Frank",
            last_name="Sinatra",
            email="frank.s@example.com",
            phone="+380912223344",
            birthday=date(1990, 10, 12),
        )
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = contact

        async def mock_execute(query):
            return mocked_result

        self.session.execute = mock_execute

        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()

        result = await self.test_instance.update_contact(self.user.id, contact_id=2, new_contact=contact_update)
        self.assertEqual(result.first_name, contact.first_name)
        self.assertEqual(result.last_name, contact.last_name)
        self.assertEqual(result.email, contact.email)
        self.assertEqual(result.phone, contact.phone)
        self.assertEqual(result.birthday, contact.birthday)

    async def test_remove_contact(self):
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = self.contact

        async def mock_execute(query):
            return mocked_result

        self.session.execute = mock_execute
        self.session.delete = AsyncMock()
        self.session.commit = AsyncMock()

        result = await self.test_instance.remove_contact(self.user.id, contact_id=2)
        self.assertEqual(result, self.contact)

    async def test_get_upcoming_birthdays(self):
        contacts = [Contact(
            id=1,
            owner_id=1,
            first_name="Tilda",
            last_name="Swinton",
            email="tilda.s@example.com",
            phone="+380923341122",
            birthday=date(1992, 12, 10),
        ), Contact(
            id=2,
            owner_id=1,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+380912223344",
            birthday=date(1990, 10, 12),
        )]
        mocked_result = MagicMock()
        mocked_result.scalars.return_value.all.return_value = contacts

        async def mock_execute(query):
            return mocked_result

        self.session.execute = mock_execute

        result = await self.test_instance.get_upcoming_birthdays(self.user.id)
        self.assertEqual(result, contacts)

