templates = [
    {
        'body': '<body>Hello {{username}}! You got {{likes_number}} likes.</body>',
        'event_type': 'likes_daily_send',
        'required_variables': ['username', 'likes_number']
    },
    {
        'body': '<body>Hello {{username}}! Click here to confirm email. {{confirmation_link}}</body>',
        'event_type': 'email_confirm_send',
        'required_variables': ['username', 'confirmation_link']
    },
]