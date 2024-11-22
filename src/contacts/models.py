from sqlalchemy import Date, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.db import Base
from src.auth.models import User


class Contact(Base):
    __tablename__ = "contact"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50), index=True)
    last_name: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    phone: Mapped[str] = mapped_column(String)
    birthday: Mapped[Date] = mapped_column(Date)
    additional_info: Mapped[str | None] = mapped_column(String(120), nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    owner: Mapped["User"] = relationship("User", back_populates="contacts")
