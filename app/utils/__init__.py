from .scraping_utils import (
    scrape_university_professors,
    replace_latin_chars,
    clean_string_for_url
)
from .request_utils import safe_request
from .data_cleaners import clean_grade, get_text_or_default

__all__ = [
    "scrape_university_professors",
    "replace_latin_chars",
    "clean_string_for_url",
    "safe_request",
    "clean_grade",
    "get_text_or_default"
]