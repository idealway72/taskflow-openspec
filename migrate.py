"""One-time migration script: creates tables in Neon PostgreSQL."""
import os
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

import ssl

load_dotenv(".env.local")

raw_url = os.environ["DATABASE_URL_UNPOOLED"]
# pg8000 dialect — strip all query params (SSL handled via connect_args)
pg8000_url = raw_url.replace("postgresql://", "postgresql+pg8000://")
pg8000_url = re.sub(r"\?.*$", "", pg8000_url)

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

print("Connecting to Neon...")

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    invite_code = Column(String(9), unique=True, nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(100), nullable=False)
    status = Column(String(10), nullable=False, default="TODO")
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (Index("ix_tasks_team_created", "team_id", "created_at"),)


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (Index("ix_messages_team_created", "team_id", "created_at"),)


engine = create_engine(pg8000_url, connect_args={"ssl_context": ssl_context})
Base.metadata.create_all(bind=engine)
print("OK: All tables created in Neon DB!")
engine.dispose()
