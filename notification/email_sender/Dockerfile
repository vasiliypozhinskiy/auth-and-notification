FROM python:3.10-slim

WORKDIR /grpc_server

RUN pip install -U pip pipenv

COPY Pipfile.lock Pipfile /grpc_server/
RUN pipenv install --deploy --system --ignore-pipfile

COPY /src /grpc_server/

CMD python email_sender_server.py