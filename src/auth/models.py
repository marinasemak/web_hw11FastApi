from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hashed: Mapped[str] = mapped_column(String)
    contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="owner")
