from datetime import datetime
from awesoon.model import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import uuid


class Prompt(Base):
    __tablename__ = "prompts"
    id = Column(Integer, primary_key=True)
    guid = Column(
        String,
        default=lambda: str(uuid.uuid4()),
    )
    prompt = Column(String)
    created_at = Column(DateTime, default=datetime.now)
