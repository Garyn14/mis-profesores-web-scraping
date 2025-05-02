from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ProfessorBase(BaseModel):
    id: str = Field(..., description="ID")
    name: str = Field(..., description="professor name")
    faculty: str = Field(..., description="faculty name")


class ProfessorStats(BaseModel):
    takeAgain: Optional[str] = Field(
        None,
        description="Percentage of students who would recommend it"
    )
    difficulty: Optional[str] = Field(
        None,
        description="Level of difficulty reported by students"
    )


class ProfessorComment(BaseModel):
    date: str = Field(..., description="comment's date")
    summary: str = Field(..., description="evaluation summary")
    overall_quality: str = Field(..., alias="overallQuality", description="general qualification")
    difficulty: str = Field(..., description="Reported difficulty level")
    course: str = Field(..., description="course of the comment")
    grade: str = Field(..., description="Rating received")
    text: str = Field(..., description="comment text")

    class Config:
        populate_by_name = True


class ProfessorResponse(ProfessorBase):
    ratings_count: int = Field(
        ...,
        alias="ratingsCount",
        description="Total number of evaluations"
    )
    average_rating: float = Field(
        ...,
        alias="averageRating",
        description="qualification average rating"
    )
    tags: List[str] = Field(
        ...,
        description="Teacher descriptive labels"
    )
    stats: ProfessorStats = Field(
        ...,
        description="Teacher Statistics"
    )

    class Config:
        populate_by_name = True


class ProfessorDetail(ProfessorResponse):
    comments: List[ProfessorComment] = Field(
        ...,
        description="List of student comments"
    )
    last_updated: datetime = Field(
        ...,
        alias="lastUpdated",
        description="Date of last data update"
    )

    class Config:
        populate_by_name = True
