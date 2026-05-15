from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    team_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    token: str
    user: UserOut


class TeamCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_length(cls, v):
        v = v.strip()
        if not v or len(v) > 30:
            raise ValueError("팀 이름은 1-30자이어야 합니다")
        return v


class TeamJoin(BaseModel):
    invite_code: str

    @field_validator("invite_code")
    @classmethod
    def code_format(cls, v):
        import re
        if not re.match(r"^[A-Z]{4}-[0-9]{4}$", v):
            raise ValueError("초대코드 형식이 올바르지 않습니다")
        return v


class TeamOut(BaseModel):
    id: int
    name: str
    invite_code: str
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MemberOut(BaseModel):
    id: int
    email: str
    is_owner: bool
    joined_at: datetime

    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    title: str
    assignee_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def title_length(cls, v):
        v = v.strip()
        if not v or len(v) > 100:
            raise ValueError("제목은 1-100자이어야 합니다")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    assignee_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def title_length(cls, v):
        if v is not None:
            v = v.strip()
            if not v or len(v) > 100:
                raise ValueError("제목은 1-100자이어야 합니다")
        return v


class TaskStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def valid_status(cls, v):
        if v not in ("TODO", "DOING", "DONE"):
            raise ValueError("status는 TODO, DOING, DONE 중 하나이어야 합니다")
        return v


class TaskOut(BaseModel):
    id: int
    team_id: int
    title: str
    status: str
    creator_id: int
    assignee_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def content_length(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("메시지를 입력해주세요")
        if len(v) > 1000:
            raise ValueError(f"메시지는 1000자 이내로 입력하세요")
        return v


class MessageOut(BaseModel):
    id: int
    user_id: int
    user_email: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
