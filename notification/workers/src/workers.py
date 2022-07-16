import grpc
import json
import logging
from abc import ABC, abstractmethod

import aio_pika
import aio_pika.abc
from jinja2 import Template
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId

from config.settings import settings
from grpc_email_sender.email_sender_pb2_grpc import EmailSenderStub
from grpc_email_sender import email_sender_pb2


logger = logging.getLogger(__name__)


class BaseWorker(ABC):
    queue_name = None

    def __init__(self, event_loop):
        self.event_loop = event_loop
        self.rabbit_connection = None
        self.db_client = None
        self.grpc_client = None

    async def connect_rabbit(self):
        self.rabbit_connection = await aio_pika.connect_robust(
            f"amqp://{settings.rabbitmq_default_user}:{settings.rabbitmq_default_pass}@rabbitmq/", loop=self.event_loop
        )

    def get_grpc_client(self):
        channel = grpc.aio.insecure_channel(f"{settings.grpc_channel_host}:{settings.grpc_channel_port}")
        self.grpc_client = EmailSenderStub(channel)

    def get_db_client(self):
        self.db_client = AsyncIOMotorClient(settings.db_host, settings.db_port)

    async def listen(self):
        async with self.rabbit_connection:
            channel: aio_pika.abc.AbstractChannel = await self.rabbit_connection.channel()

            queue: aio_pika.abc.AbstractQueue = await channel.get_queue(
                self.queue_name
            )

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process(ignore_processed=True):
                        try:
                            message_body = json.loads(message.body.decode())
                            processed_message_body = await self.process_message_body(message_body)
                            await self.grpc_client.SendEmail(
                                email_sender_pb2.SendEmailRequest(
                                    email=message_body['email'],
                                    email_body=processed_message_body
                                )
                            )
                            await message.ack()
                        except (self.TemplateNotFoundException, self.TemplateKeyNotFoundException):
                            await message.reject()
                        except grpc.RpcError as err:
                            if err.code() == grpc.StatusCode.CANCELLED:
                                await message.nack()
                            else:
                                await message.reject()

    async def prepare(self):
        await self.connect_rabbit()
        self.get_db_client()
        self.get_grpc_client()

    async def run(self):
        await self.prepare()
        await self.listen()

    @abstractmethod
    async def process_message_body(self, message):
        pass

    class TemplateNotFoundException(Exception):
        pass

    class TemplateKeyNotFoundException(Exception):
        pass

    class WrongWorkerConfigException(Exception):
        pass


class BaseTemplateWorker(BaseWorker):

    def __init__(self, event_loop, queue_name, event_type):
        super().__init__(event_loop)
        self.queue_name = queue_name
        self.event_type = event_type

    async def process_message_body(self, message):
        collection = self.db_client.notification.templates

        if isinstance(self, DefaultTemplateWorker):
            template = await self.get_template(collection, self.event_type)
        elif isinstance(self, CustomTemplateWorker):
            template = await self.get_template(collection, message['template_id'])
        else:
            raise self.WrongWorkerConfigException

        if not template:
            raise self.TemplateNotFoundException

        template_data = {}
        for variable in template['required_variables']:
            try:
                template_data[variable] = message[variable]
            except KeyError:
                logger.error(f"Can't get required variable {variable} from message")
                raise self.TemplateKeyNotFoundException

        jinja_template = Template(template['body'])
        logger.warning(jinja_template.render(template_data))

        return jinja_template.render(template_data)

    @abstractmethod
    async def get_template(self, collection, value):
        pass


class DefaultTemplateWorker(BaseTemplateWorker):
    async def get_template(self, collection, event_type):
        return await collection.find_one({'event_type': event_type})


class CustomTemplateWorker(BaseTemplateWorker):
    async def get_template(self, collection, template_id):
        return await collection.find_one({'_id': ObjectId(template_id)})