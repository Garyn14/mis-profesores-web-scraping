# Professor Ratings Scraper API

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green?logo=fastapi)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.12+-lightgrey?logo=beautifulsoup)

A high-performance web scraping API that collects professor rating data with elegant progress tracking.

## Features

- 🚀 Async-powered scraping and data processing
- 📊 Real-time console progress visualization
- 🔍 Automatic caching with configurable TTL
- 🛡️ Robust error handling and retry logic
- 📝 Pydantic-validated response models
- 🎨 Colorful console logging with emojis

## Technologies Used

- **Framework**: FastAPI
- **Scraping**: BeautifulSoup4, Requests
- **Validation**: Pydantic v2
- **Caching**: CacheTools
- **Logging**: Colorlog

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/professor-scraper.git
cd professor-scraper
```
2. Install dependencies (Poetry recommended):
```bash
poetry install
```

3. Create .env file:
```bash
UNIVERSITY_URL=https://peru.misprofesores.com/escuelas/Universidad-Nacional-de-San-Marcos_1135
CACHE_TTL=3600
```

## Usage
Start the development server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

Get all professors:
```bash
GET /profesores/all
```

Get paginated results:
```bash
GET /profesores?limit=50&offset=100
```

Health check:
```bash
GET /health
```

## Example Console Output
```bash
INFO     🚀 Starting application...
INFO     🌐 GET /profesores/all request received
INFO     🔄 Processing data...
INFO     📊 Processing 646 professors...
Progreso: |██████████████████████████████████████████████████| 100.0% 646/646
INFO     ✅ Processing completed: 646/646 records in 1.40s
INFO     📡 Sending response: 200 OK
```

## Project Structure
```bash
professor-scraper/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   └── profesores.py
│   │   └── schemas/
│   │       └── profesores.py
│   ├── core/
│   ├── services/
│   └── utils/
├── .env
└── pyproject.toml
```