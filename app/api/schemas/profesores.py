from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ProfessorBase(BaseModel):
    id: str = Field(..., description="ID único del profesor")
    name: str = Field(..., description="Nombre completo del profesor")
    faculty: str = Field(..., description="Facultad a la que pertenece")

class ProfessorStats(BaseModel):
    takeAgain: Optional[str] = Field(
        None,
        description="Porcentaje de estudiantes que lo recomendarían"
    )
    difficulty: Optional[str] = Field(
        None,
        description="Nivel de dificultad reportado por estudiantes"
    )

class ProfessorComment(BaseModel):
    date: str = Field(..., description="Fecha del comentario")
    summary: str = Field(..., description="Resumen de la evaluación")
    overall_quality: str = Field(..., alias="overallQuality", description="Calificación general")
    difficulty: str = Field(..., description="Nivel de dificultad reportado")
    course: str = Field(..., description="Curso relacionado al comentario")
    grade: str = Field(..., description="Calificación recibida")
    text: str = Field(..., description="Texto completo del comentario")

    class Config:
        populate_by_name = True

class ProfessorResponse(ProfessorBase):
    ratings_count: int = Field(
        ...,
        alias="ratingsCount",
        description="Número total de evaluaciones"
    )
    average_rating: float = Field(
        ...,
        alias="averageRating",
        description="Calificación promedio"
    )
    tags: List[str] = Field(
        ...,
        description="Etiquetas descriptivas del profesor"
    )
    stats: ProfessorStats = Field(
        ...,
        description="Estadísticas del profesor"
    )

    class Config:
        populate_by_name = True

class ProfessorDetail(ProfessorResponse):
    comments: List[ProfessorComment] = Field(
        ...,
        description="Lista de comentarios de estudiantes"
    )
    last_updated: datetime = Field(
        ...,
        alias="lastUpdated",
        description="Fecha de última actualización de datos"
    )

    class Config:
        populate_by_name = True