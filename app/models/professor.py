"""Data models for professors"""
from typing import List, Dict, Optional
from pydantic import BaseModel

class ProfessorStats(BaseModel):
    takeAgain: Optional[str] = None
    difficulty: Optional[str] = None

class ProfessorComment(BaseModel):
    date: str
    summary: str
    overall_quality: str
    difficulty: str
    course: str
    grade: str
    text: str
    professor_id: Optional[str] = None
    professor_name: Optional[str] = None

class Professor(BaseModel):
    id: str
    name: str
    faculty: str
    ratings_count: int
    average_rating: float
    profile_url: str
    comments_url: str
    tags: List[str] = []
    stats: ProfessorStats = ProfessorStats()
    comments: List[ProfessorComment] = []