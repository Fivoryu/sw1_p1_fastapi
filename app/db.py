import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient

class MongoConnection:
    def __init__(self, uri: str | None = None, db_name: str | None = None):
        self._uri = uri or os.getenv("MONGO_URI")
        self._db_name = db_name or os.getenv("MONGO_DB") or "workflow1"
        self.client: AsyncIOMotorClient | None = None
        self.db = None
        self.last_error: str | None = None

    async def connect(self, app=None):
        if not self._uri:
            if app is not None:
                app.state.mongo_client = None
                app.state.mongodb = None
                app.state.mongo_error = "not-configured"
            return

        try:
            self.client = AsyncIOMotorClient(self._uri, tlsCAFile=certifi.where())
            self.db = self.client[self._db_name]
            await self.client.admin.command("ping")
            self.last_error = None
            if app is not None:
                app.state.mongo_client = self.client
                app.state.mongodb = self.db
                app.state.mongo_error = None
        except Exception as exc:
            self.last_error = str(exc)
            if self.client:
                self.client.close()
            self.client = None
            self.db = None
            if app is not None:
                app.state.mongo_client = None
                app.state.mongodb = None
                app.state.mongo_error = self.last_error

    def close(self):
        if self.client:
            self.client.close()


mongo = MongoConnection()
