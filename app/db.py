import os
from motor.motor_asyncio import AsyncIOMotorClient

class MongoConnection:
    def __init__(self, uri: str | None = None, db_name: str | None = None):
        self._uri = uri or os.getenv("MONGO_URI")
        self._db_name = db_name or os.getenv("MONGO_DB") or "workflow1"
        self.client: AsyncIOMotorClient | None = None
        self.db = None

    async def connect(self, app=None):
        if not self._uri:
            if app is not None:
                app.state.mongo_client = None
                app.state.mongodb = None
            return

        self.client = AsyncIOMotorClient(self._uri)
        self.db = self.client[self._db_name]
        if app is not None:
            app.state.mongo_client = self.client
            app.state.mongodb = self.db
        # Verify connection
        await self.client.admin.command("ping")

    def close(self):
        if self.client:
            self.client.close()


mongo = MongoConnection()
