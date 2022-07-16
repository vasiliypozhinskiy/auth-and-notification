from concurrent import futures
import logging
import smtplib
from email.message import EmailMessage
from abc import ABC, abstractmethod

import grpc

import email_sender_pb2
import email_sender_pb2_grpc
from config import config

logger = logging.getLogger(__name__)


class BaseEmailSender(ABC):

    @abstractmethod
    def prepare(self):
        pass

    @abstractmethod
    def SendEmail(self, request, context):
        pass


class SMTPEmailSender(BaseEmailSender, email_sender_pb2_grpc.EmailSenderServicer):
    email_server = None

    def prepare(self):
        self.email_server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
        self.email_server.login(config['mail_user'], config['mail_password'])

    def SendEmail(self, request, context):
        logger.warning(request.email)
        logger.warning(request.email_body)

        message = EmailMessage()
        message["From"] = config['mail_user']
        message["To"] = request.email
        message["Subject"] = 'Привет!'

        message.add_alternative(request.email_body, subtype='html')
        try:
            self.email_server.sendmail(config['mail_user'], [request.email], message.as_string())
        except Exception:
            context.set_code(grpc.StatusCode.CANCELLED)

        return email_sender_pb2.SendEmailReply()


def get_email_sender():
    return SMTPEmailSender()


if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    email_sender = get_email_sender()
    email_sender.prepare()

    email_sender_pb2_grpc.add_EmailSenderServicer_to_server(email_sender, server)
    server.add_insecure_port('[::]:50055')
    server.start()
    server.wait_for_termination()
