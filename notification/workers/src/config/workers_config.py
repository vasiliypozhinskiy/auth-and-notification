from workers import CustomTemplateWorker, DefaultTemplateWorker


workers_config = [
    {'class': DefaultTemplateWorker, 'event_type': 'email_confirm_send', 'queue_name': 'email_confirm_send'},
    {'class': DefaultTemplateWorker, 'event_type': 'email_confirm_send', 'queue_name': 'dead_email_confirm_send'},
    {'class': DefaultTemplateWorker, 'event_type': 'likes_daily_send', 'queue_name': 'likes_daily_send'},
    {'class': DefaultTemplateWorker, 'event_type': 'likes_daily_send', 'queue_name': 'dead_likes_daily_send'},
    {'class': CustomTemplateWorker, 'event_type': 'thematic_send', 'queue_name': 'thematic_send'},
    {'class': CustomTemplateWorker, 'event_type': 'thematic_send', 'queue_name': 'dead_thematic_send'}
]