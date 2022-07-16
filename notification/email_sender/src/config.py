import os

config = {
    "mail_user": os.getenv('EMAIL_LOGIN'),
    "mail_password": os.getenv('EMAIL_PASSWORD')
}
