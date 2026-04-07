from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

# Initialize MongoDB Client
client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB_NAME]

async def get_db():
    """Dependency for getting MongoDB database instance"""
    yield db