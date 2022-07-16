from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic.main import BaseModel


class UserResponse(BaseModel):
    login: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    birthdate: Optional[str]
    roles: Optional[List[str]]


class HistoryEntry(BaseModel):
    id: UUID
    user_agent: str
    created_at: datetime


class UserHistoryResponse(BaseModel):
    entries: List[HistoryEntry]

    def to_dict(self):
        return {"entries": [dict(entry) for entry in self.entries]}
