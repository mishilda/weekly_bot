from sqlalchemy import String, Text, DateTime, Boolean, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


class UserDb(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=True)
    role: Mapped[str] = mapped_column(String(10), nullable=True)
    chat_id: Mapped[int] = mapped_column(nullable=True)
    is_mute: Mapped[bool] = mapped_column(Boolean, default=False)


class MessageDb(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    private_id: Mapped[int] = mapped_column(nullable=False)
    private_chat: Mapped[int] = mapped_column(nullable=False)
    topic_id: Mapped[int] = mapped_column(nullable=False)
    topic_chat: Mapped[int] = mapped_column(nullable=False)
    # text: Mapped[str] = mapped_column(Text)
