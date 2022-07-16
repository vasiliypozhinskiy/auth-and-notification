import backoff
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

import logger

_logger = logger.logging.getLogger(__name__)


class NotificationsConsumer:

    def __init__(self, connection_settings: dict):
        """
        Mongo Consumer class.

        :param connection_settings: connection settings.
        Dict with key:value - host:str, port:int, database:str, collection:str
        """
        self.connection_settings = connection_settings
        self._client = None
        self._cursor = None
        self._documents_to_update = None

    @backoff.on_exception(backoff.expo, ServerSelectionTimeoutError)
    def _get_client(self):
        """Create Mongo client."""
        self._client = MongoClient(
            host=self.connection_settings["host"],
            port=self.connection_settings["port"],
            serverSelectionTimeoutMS=10000
        )
        self._client.server_info()

    @backoff.on_exception(backoff.expo, ServerSelectionTimeoutError)
    def _get_cursor(self):
        """Create Mongo cursor."""
        self._get_client()
        self._cursor = self._client[self.connection_settings["database"]][
            self.connection_settings["collection"]]

    @backoff.on_exception(backoff.expo, ServerSelectionTimeoutError)
    def _update(self):
        """Updated sent notification."""
        if self._documents_to_update:
            self._get_cursor()
            self._cursor.update_many(
                {"$or": self._documents_to_update},
                {"$currentDate": {"sent_to_rabbit_at": True}},
                upsert=True
            )
            self._client.close()

    @backoff.on_exception(backoff.expo, ServerSelectionTimeoutError)
    def get_batch_for_time_zone(self, time_zone: int):
        """Get batches of documents for time_zone."""
        offset = 0
        size = 100
        is_over = False
        _filter = {"time_zone": time_zone, "$where": "this.updated_at > this.sent_to_rabbit_at"}
        self._documents_to_update = []
        self._get_cursor()
        while not is_over:
            batch = self._cursor.find(_filter).skip(offset).limit(size).sort("updated_at")
            batch = list(batch)
            if not batch:
                break
            if len(batch) < size:
                is_over = True
            documents_for_update = [{"_id": x["_id"]} for x in batch]
            self._documents_to_update.extend(documents_for_update)
            offset += size
            yield batch
        self._client.close()
        self._update()

    def get_count_documents(self, time_zone: int) -> int:
        """Function to count documents for publish."""
        self._get_cursor()
        _filter = {"time_zone": time_zone, "$expr": {"$gt": ["$updated_at", "$sent_to_rabbit_at"]}}
        count = self._cursor.count_documents(_filter)
        self._client.close()
        print("Docs {} in {}".format(self.connection_settings["collection"], count))
        return count
