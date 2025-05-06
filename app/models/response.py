"""Response models for API"""
from typing import List
from pydantic import BaseModel
from app.models.professor import Professor

class HealthCheck(BaseModel):
    status: str
    version: str

class ProfessorsResponse(BaseModel):
    professors: List[Professor]
    count: int