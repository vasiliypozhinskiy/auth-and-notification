#!/usr/local/bin/python
import datetime

import logger
import scheduler_config
from mongo_consumer import NotificationsConsumer
from rabbit_publisher import EmailRabbitPublisher

_logger = logger.logging.getLogger(__name__)


def get_time_zone_for_notifications(_time: str) -> int:
    """
    Function return time zone where <time> at current moment.

    :param _time: time for notification.
    """
    time_for_notification = datetime.datetime.strptime(_time, "%I:%M%p")
    current_time = datetime.datetime.utcnow()
    return time_for_notification.hour - current_time.hour


def publishing_notification(time_zone, mongo_params, rabbit_params):
    """
    Function count documents in collection for time_zone and publish in rabbitmq if nessery

    :param time_zone: time_zone for notification.
    """
    mongo = NotificationsConsumer(connection_settings=mongo_params)
    count_documents = mongo.get_count_documents(time_zone)
    if not count_documents:
        return
    queryset_generator = mongo.get_batch_for_time_zone(time_zone)
    publisher = EmailRabbitPublisher(connection_settings=rabbit_params, mongo_cursor=queryset_generator)
    publisher.run_publish()


def main():
    time_zone = get_time_zone_for_notifications(scheduler_config.TIME_FOR_NOTIFICATION)
    print("TIME ZONE {}".format(time_zone))
    for i in scheduler_config.MONGO_PARAMS:
        publishing_notification(
            time_zone, mongo_params=scheduler_config.MONGO_PARAMS[i],
            rabbit_params=scheduler_config.RABBIT_PARAMS
        )


if __name__ == '__main__':
    _logger.info("start")
    main()
