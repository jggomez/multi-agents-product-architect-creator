from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class UserStory(BaseModel):
    id: str = Field(..., description="Unique identifier for the user story (e.g. US-001)")
    title: str = Field(..., description="Short title of the user story")
    requirement: str = Field(..., description="The 'I want to...' part")
    benefit: str = Field(..., description="The 'So that...' part")
    acceptance_criteria: List[str] = Field(default_factory=list, description="List of conditions to satisfy")

class UserStoryArtifact(BaseModel):
    goal_id: str
    stories: List[UserStory]
    metadata: Optional[dict] = None

class ADRStatus(str, Enum):
    PROPOSED = "Proposed"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    SUPERSEDED = "Superseded"

class ADR(BaseModel):
    id: str = Field(..., description="Unique identifier for the ADR (e.g. ADR-001)")
    title: str = Field(..., description="Title of the technical decision")
    context: str = Field(..., description="The problem or context")
    decision: str = Field(..., description="The decision made")
    status: ADRStatus = Field(default=ADRStatus.PROPOSED)
    rationale: str = Field(..., description="Why this decision was made")
    consequences: str = Field(..., description="Impact of the decision")

class ADRArtifact(BaseModel):
    stories_ref: str
    adrs: List[ADR]
    patterns: List[str]
    metadata: Optional[dict] = None
