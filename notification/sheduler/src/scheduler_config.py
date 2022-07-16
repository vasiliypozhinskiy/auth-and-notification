TIME_FOR_NOTIFICATION = "12:00PM"

MONGO_PARAMS = {
    "daily": {"host": "notification_db", "port": 27017, "database": "notifications", "collection": "regular"},
    "thematic": {"host": "notification_db", "port": 27017, "database": "notifications", "collection": "thematic"}
}

RABBIT_PARAMS = {"host": "rabbitmq", "port": 5672, "exchange": "email_notification"}
