ARG WORK_DIR=/workers
FROM python:3.10-slim as python_base

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait

ARG WORK_DIR
WORKDIR $WORK_DIR
RUN pip install -U pip pipenv

FROM python_base as dev
COPY Pipfile.lock Pipfile ./
RUN pipenv install --deploy --system --ignore-pipfile

CMD /wait && python ./src/main.py