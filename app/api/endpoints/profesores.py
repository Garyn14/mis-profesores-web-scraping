from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.services.scraping_service import (
    get_professors_data,
    refresh_professors_data,
    get_professor_by_id
)
from app.api.schemas.profesores import (
    ProfessorResponse,
    ProfessorDetail
)
from app.api.dependencies import verify_token

router = APIRouter(prefix="/profesores", tags=["profesores"])

@router.get("/", response_model=List[ProfessorResponse])
async def list_professors(
    limit: Optional[int] = Query(100, ge=1, le=1000),
    offset: Optional[int] = Query(0, ge=0)
):
    """Obtiene todos los profesores con paginación"""
    professors = await get_professors_data()
    return professors[offset:offset + limit]

@router.get("/search", response_model=List[ProfessorResponse])
async def search_professors(
    query: str = Query(..., min_length=2, max_length=50),
    limit: Optional[int] = Query(10, ge=1, le=50)
):
    """Busca profesores por nombre o facultad"""
    professors = await get_professors_data()
    results = [
        p for p in professors
        if query.lower() in p.name.lower() or
           query.lower() in p.faculty.lower()
    ]
    return results[:limit]

@router.get("/{professor_id}", response_model=ProfessorDetail)
async def get_professor(professor_id: str):
    """Obtiene un profesor específico por ID con todos sus detalles"""
    professor = await get_professor_by_id(professor_id)
    if not professor:
        raise HTTPException(
            status_code=404,
            detail="Professor not found"
        )
    return professor

@router.post("/refresh", dependencies=[Depends(verify_token)])
async def refresh_data():
    """Fuerza la actualización de los datos (requiere autenticación)"""
    await refresh_professors_data()
    return {"status": "data refreshed"}