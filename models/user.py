from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True,nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)

    profile = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        lazy="selectin",
        cascade="all, delete-orphan"
    )