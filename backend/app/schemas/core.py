from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class ProjectUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    created_at: datetime


class MessageIn(BaseModel):
    role: Literal["user", "assistant", "tool"]
    content: str = Field(min_length=1, max_length=100_000)
    authored_by: Literal["ai", "user"] | None = None
    code_diff: str | None = Field(default=None, max_length=200_000)
    timestamp: datetime | None = None


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    role: str
    content: str
    authored_by: str | None
    code_diff: str | None
    timestamp: datetime


class SessionCreate(BaseModel):
    project_id: str | None = None
    source_tool: str = Field(default="native", max_length=50)
    title: str | None = Field(default=None, max_length=300)


class SessionImport(BaseModel):
    """Paste/import an external coding session (wrapped fidelity)."""

    project_id: str | None = None
    source_tool: Literal["claude_code", "cursor", "copilot", "chatgpt", "other"] = "other"
    title: str | None = Field(default=None, max_length=300)
    messages: list[MessageIn] = Field(min_length=1, max_length=500)
    raw_text: str | None = Field(default=None, max_length=500_000)


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str | None
    source_tool: str
    source_fidelity: str
    title: str | None
    started_at: datetime
    ended_at: datetime | None
    extraction_status: str
    created_at: datetime


class SessionDetailOut(SessionOut):
    messages: list[MessageOut]


class AgentChatRequest(BaseModel):
    session_id: str | None = None
    project_id: str | None = None
    message: str = Field(min_length=1, max_length=50_000)
    code_context: str | None = Field(default=None, max_length=100_000)


class AgentChatResponse(BaseModel):
    session_id: str
    user_message: MessageOut
    assistant_message: MessageOut
