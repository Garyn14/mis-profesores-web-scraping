from pydantic import BaseModel

class UniversityResponse(BaseModel):
    name: str
    url: str
    professor_count: int