from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.core.config import settings

security = HTTPBearer()

async def verify_token(credentials: HTTPBearer = Depends(security)):
    """Dependencia para autenticación (ejemplo)"""
    if credentials.credentials != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return credentials.credentials