from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeUnitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str | None
    session_id: str | None
    source_fidelity: str
    unit_type: str
    title: str
    summary: str | None
    difficulty: str | None
    extracted_at: datetime


class LearnRequest(BaseModel):
    scope_type: Literal["message", "chat", "project", "time_range"]
    # scope refs — exactly the relevant one must be provided for the scope_type
    message_id: str | None = None
    session_id: str | None = None
    project_id: str | None = None
    time_start: datetime | None = None
    time_end: datetime | None = None


class ArtifactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    scope_type: str
    scope_ref: dict
    format: str
    content: dict
    generated_at: datetime
    triggered_by: str
    completed_at: datetime | None


class LearnResponse(BaseModel):
    artifacts: list[ArtifactOut]
    units_covered: int
    message: str | None = None


class ReviewQueueItem(BaseModel):
    unit: KnowledgeUnitOut
    artifact: ArtifactOut
    review_state_id: str
    mastery_status: str
    next_review_at: datetime
    early: bool = False


class ReviewQueueOut(BaseModel):
    items: list[ReviewQueueItem]
    total_due: int
    total_early: int = 0
    projects_in_session: int
    next_due_at: datetime | None = None


class ReviewSubmission(BaseModel):
    unit_id: str
    artifact_id: str | None = None
    performance: Literal["correct", "partial", "incorrect"]
    response_text: str | None = Field(default=None, max_length=20_000)
    early: bool = False  # explicit opt-in to review inside the consolidation window


class ReviewResultOut(BaseModel):
    unit_id: str
    mastery_status: str
    next_review_at: datetime
    interval_days: float
    ease_factor: float


class ProfileEntryOut(BaseModel):
    unit: KnowledgeUnitOut
    mastery_status: str
    retention_trend: str | None
    visibility: str
    entry_id: str


class ProfileOut(BaseModel):
    entries: list[ProfileEntryOut]
    counts: dict
    generated_at: datetime


class VisibilityUpdate(BaseModel):
    visibility: Literal["private", "shared"]
