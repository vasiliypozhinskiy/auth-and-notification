import json
import time

import backoff
from pika import PlainCredentials, ConnectionParameters, BlockingConnection, BasicProperties
from pika.exceptions import UnroutableError, AMQPConnectionError, ConnectionClosedByBroker
from pymongo import MongoClient

import logger

_logger = logger.logging.getLogger(__name__)


class EmailRabbitPublisher:

    def __init__(self, connection_settings: dict, mongo_cursor: MongoClient):
        """
        Rabbit Publisher class.

        :param connection_settings: connection settings.
        Dict with key:value - host:str, port:int, exchange:str
        """
        self.connection_settings = connection_settings
        self._messages = None
        self._mongo_cursor = mongo_cursor
        self._connection = None
        self._channel = None
        self._not_delivery_messages = None

    @backoff.on_exception(backoff.expo, (AMQPConnectionError, ConnectionClosedByBroker))
    def _get_connection(self):
        """Get blocking connection to rabbit."""
        credentials = PlainCredentials('notification_admin', 'as1234')
        conn_params = ConnectionParameters(
            host=self.connection_settings["host"], port=self.connection_settings["port"], credentials=credentials
        )
        self._connection = BlockingConnection(conn_params)

    @backoff.on_exception(backoff.expo, (AMQPConnectionError, ConnectionClosedByBroker))
    def _get_channel(self):
        """Open channel."""
        self._get_connection()
        self._channel = self._connection.channel()
        self._channel.confirm_delivery()

    def _publish_messages(self, message):
        """Publish single message."""
        properties = BasicProperties(
            app_id='example-publisher', content_type='application/json',
            headers={"request_id": message["x_request_id"]}, delivery_mode=2
        )
        try:
            self._channel.basic_publish(
                self.connection_settings["exchange"], message["event"], json.dumps(message["data"]).encode("utf-8"),
                properties, mandatory=True
            )
        except UnroutableError:
            self._not_delivery_messages.append(message)

    def _stop(self):
        self._channel.close()
        self._connection.close()

    @backoff.on_exception(backoff.expo, (AMQPConnectionError, ConnectionClosedByBroker))
    def run_publish(self):
        """Main method to publish messeages."""
        self._get_channel()
        if not self._not_delivery_messages:
            self._not_delivery_messages = []
        counter = 0
        while True:
            if not self._messages:
                try:
                    self._messages = self._mongo_cursor.__next__()
                except StopIteration:
                    if not self._not_delivery_messages:
                        break
                    self._messages = self._not_delivery_messages[:]
                    self._not_delivery_messages = []
                    time.sleep(5)
            message = self._messages.pop(0)
            self._publish_messages(message)
            counter += 1
        self._stop()
        print(counter)
