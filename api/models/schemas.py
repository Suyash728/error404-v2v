"""Pydantic models matching supabase/migrations/001_init.sql.

Convention: `*Create` models hold only client-editable fields. Identity
columns (id/user_id) and server-assigned timestamps are never accepted from
a request body — they come from the verified JWT (core.security) or a
database default, and only appear on the read models.
"""

import uuid
from datetime import date, datetime, time
from typing import Literal, Optional

from pydantic import BaseModel, Field

from constants import Symptom

IntentionMode = Literal["track", "avoid", "ttc"]
ReminderKind = Literal["period", "fertile", "contraception", "appointment"]
CyclePhaseName = Literal["menstrual", "follicular", "ovulatory", "luteal"]
ConfidenceLevel = Literal["high", "medium", "low"]


class ProfileBase(BaseModel):
    name: Optional[str] = None
    avg_cycle_len: int = 28
    avg_period_len: int = 5
    last_period_start: Optional[date] = None
    language_pref: str = "en"
    intention_mode: IntentionMode = "track"
    gcal_connected: bool = False
    gfit_connected: bool = False


class ProfileCreate(ProfileBase):
    pass


class Profile(ProfileBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class CycleBase(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    length: Optional[int] = None


class CycleCreate(CycleBase):
    pass


class Cycle(CycleBase):
    id: uuid.UUID
    user_id: uuid.UUID

    model_config = {"from_attributes": True}


class FertileWindow(BaseModel):
    start: date
    end: date


class Prediction(BaseModel):
    next_period_start: date
    fertile_window: FertileWindow
    current_phase: CyclePhaseName
    cycle_day: int
    cycle_length: int
    confidence: ConfidenceLevel


class WorkoutContent(BaseModel):
    intensity_label: str
    plan: list[str]
    avoid: str


class NutritionContent(BaseModel):
    focus: str
    foods: list[str]
    tip: str


class PhaseContent(BaseModel):
    phase_summary: str
    workout: WorkoutContent
    nutrition: NutritionContent


class RecommendationsResponse(BaseModel):
    phase: CyclePhaseName
    cycle_day: int
    content: PhaseContent
    adaptive_line: Optional[str] = None
    disclaimer: str


class DailyLogBase(BaseModel):
    log_date: date
    flow: Optional[int] = Field(default=None, ge=0, le=4)
    symptoms: list[Symptom] = Field(default_factory=list)
    mood: Optional[int] = Field(default=None, ge=1, le=5)
    energy: Optional[int] = Field(default=None, ge=1, le=5)
    water_ml: Optional[int] = Field(default=None, ge=0)
    bbt: Optional[float] = None
    notes: Optional[str] = None


class DailyLogCreate(DailyLogBase):
    pass


class DailyLog(DailyLogBase):
    id: uuid.UUID
    user_id: uuid.UUID

    model_config = {"from_attributes": True}


class ReproductiveLogBase(BaseModel):
    log_date: date
    contraception_taken: Optional[bool] = None
    cervical_mucus: Optional[str] = None
    intercourse: Optional[bool] = None
    notes: Optional[str] = None


class ReproductiveLogCreate(ReproductiveLogBase):
    pass


class ReproductiveLog(ReproductiveLogBase):
    id: uuid.UUID
    user_id: uuid.UUID

    model_config = {"from_attributes": True}


class ReminderBase(BaseModel):
    kind: ReminderKind
    title: str
    time_of_day: Optional[time] = None
    frequency: Optional[str] = None
    gcal_event_id: Optional[str] = None
    discreet: bool = False


class ReminderCreate(ReminderBase):
    pass


class Reminder(ReminderBase):
    id: uuid.UUID
    user_id: uuid.UUID

    model_config = {"from_attributes": True}


class RiskFlagBase(BaseModel):
    flag_type: str
    severity: str
    fired_rules: list[str] = Field(default_factory=list)
    explanation: Optional[str] = None
    llm_provider: Optional[str] = None


class RiskFlagCreate(RiskFlagBase):
    pass


class RiskFlag(RiskFlagBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class GamificationBase(BaseModel):
    petals: int = 0
    level: Optional[str] = None
    streak_count: int = 0
    streak_freeze_used: bool = False
    last_checkin: Optional[date] = None


class GamificationCreate(GamificationBase):
    pass


class Gamification(GamificationBase):
    user_id: uuid.UUID

    model_config = {"from_attributes": True}


class BadgeBase(BaseModel):
    badge_key: str


class BadgeCreate(BadgeBase):
    pass


class Badge(BadgeBase):
    id: uuid.UUID
    user_id: uuid.UUID
    earned_at: datetime

    model_config = {"from_attributes": True}


class FitSnapshotBase(BaseModel):
    date: date
    steps: Optional[int] = None
    active_min: Optional[int] = None
    sleep_min: Optional[int] = None
    avg_hr: Optional[int] = None


class FitSnapshotCreate(FitSnapshotBase):
    pass


class FitSnapshot(FitSnapshotBase):
    id: uuid.UUID
    user_id: uuid.UUID

    model_config = {"from_attributes": True}


class RagDocumentBase(BaseModel):
    title: str
    source_org: Optional[str] = None


class RagDocumentCreate(RagDocumentBase):
    pass


class RagDocument(RagDocumentBase):
    id: uuid.UUID

    model_config = {"from_attributes": True}


class RagChunkBase(BaseModel):
    doc_id: uuid.UUID
    content: str
    embedding: Optional[list[float]] = None


class RagChunkCreate(RagChunkBase):
    pass


class RagChunk(RagChunkBase):
    id: uuid.UUID

    model_config = {"from_attributes": True}
