import asyncio
import logging
from multiprocessing import Process

from pymongo import MongoClient

from config.settings import settings
from config.workers_config import workers_config
from base_templates import templates

logger = logging.getLogger(__name__)


def prepare_templates():
    client = MongoClient(settings.db_host, settings.db_port)

    collection = client.notification.templates

    for default_template in templates:
        template = collection.find_one({'event_type': default_template['event_type']})

        if not template:
            collection.insert_one(default_template)
            logger.warning(f'Template {default_template["event_type"]} loaded.')


def run_worker(worker_config):
    loop = asyncio.new_event_loop()
    current_worker = worker_config['class'](loop, worker_config['queue_name'], worker_config['event_type'])
    loop.run_until_complete(current_worker.run())


if __name__ == "__main__":
    prepare_templates()

    processes = []

    for worker_settings in workers_config:
        process = Process(target=run_worker, args=(worker_settings,))
        processes.append(process)

    for process in processes:
        process.start()


