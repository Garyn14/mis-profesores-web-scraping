from typing import Any, Optional
from bs4 import BeautifulSoup, Tag


def clean_grade(grade: str) -> str:
    """Limpia el texto de la calificación."""
    return grade.replace('Calificación Recibida: ', '') if grade != 'N/A' else grade


def get_text_or_default(element: Optional[Any], selector: str, index: int = None) -> str:
    """Helper para extraer texto o devolver 'N/A' si no existe."""
    if element is None:
        return 'N/A'

    found = element.select(selector)
    if not found:
        return 'N/A'
    if index is not None:
        return found[index].get_text(strip=True) if len(found) > index else 'N/A'
    return found[0].get_text(strip=True)