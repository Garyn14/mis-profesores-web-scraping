import asyncio
from app.services.scraping_service import refresh_professors_data
from app.core.logger import logger

async def main():
    logger.info("Starting initial data scrape...")
    professors = await refresh_professors_data()
    logger.info(f"Scraped {len(professors)} professors")

if __name__ == "__main__":
    asyncio.run(main())