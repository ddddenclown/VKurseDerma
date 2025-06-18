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

    friendships_initiated = relationship(
        "Friendship",
        foreign_keys="Friendship.user_id",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    friendships_received = relationship(
        "Friendship",
        foreign_keys="Friendship.friend_id",
        back_populates="friend",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    @property
    def friends(self):
        accepted_initiated =[f.friend for f in self.friendships_initiated if f.status == "accepted"]
        accepted_received = [f.user for f in self.friendships_received if f.status == "accepted"]

        return list(set(accepted_initiated+ accepted_received))

    @property
    def pending_requests(self):
        return [f.user for f in self.friendships_received if f.status == "pending"]