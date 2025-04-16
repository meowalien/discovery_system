from sqlalchemy import Integer, Text, LargeBinary, BigInteger, String, ForeignKey, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Optional
from uuid import UUID as UUIDType


class Base(DeclarativeBase):
    pass

class SessionModel(Base):
    __tablename__ = "sessions"
    __table_args__ = {"schema": "telegram_reader"}

    # 使用者唯一識別：用 Text 作為主鍵
    session_id: Mapped[str] = mapped_column(Text, primary_key=True)
    dc_id: Mapped[int] = mapped_column(Integer)
    server_address: Mapped[str] = mapped_column(Text)
    port: Mapped[int] = mapped_column(Integer)
    # 若 auth_key 未必有值，可使用 Optional[bytes]
    auth_key: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    takeout_id: Mapped[Optional[int]] = mapped_column(Integer)


class Entity(Base):
    __tablename__ = "entities"
    __table_args__ = {"schema": "telegram_reader"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    hash: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[int]] = mapped_column(BigInteger)
    name: Mapped[Optional[str]] = mapped_column(Text)
    date: Mapped[Optional[int]] = mapped_column(Integer)


class SentFile(Base):
    __tablename__ = "sent_files"
    __table_args__ = {"schema": "telegram_reader"}

    md5_digest: Mapped[bytes] = mapped_column(LargeBinary, primary_key=True)
    file_size: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[int] = mapped_column(Integer, primary_key=True)
    id: Mapped[Optional[int]] = mapped_column(Integer)
    hash: Mapped[Optional[int]] = mapped_column(Integer)


class UpdateState(Base):
    __tablename__ = "update_state"
    __table_args__ = {"schema": "telegram_reader"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pts: Mapped[int] = mapped_column(Integer)
    qts: Mapped[int] = mapped_column(Integer)
    date: Mapped[int] = mapped_column(Integer)
    seq: Mapped[int] = mapped_column(Integer)



class KeycloakUserEntity(Base):
    __tablename__ = "user_entity"
    __table_args__ = {"schema": "keycloak"}
    id:Mapped[str] = mapped_column(String(36), primary_key=True)






