from motor import motor_asyncio

MONGO_CLIENT = None


def get_mongo_client() -> motor_asyncio.AsyncIOMotorClient | None:
    return MONGO_CLIENT