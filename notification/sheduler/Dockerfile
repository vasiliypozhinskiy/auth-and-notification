FROM python:3.10-slim
COPY ./src /app
COPY crontab /etc/cron.d/crontab
WORKDIR /app
RUN apt-get update && apt-get -y install cron vim
RUN pip install -U pip pipenv
COPY Pipfile.lock Pipfile ./
RUN pipenv install --deploy --system --dev --ignore-pipfile
RUN chmod 0744 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab

CMD ["cron", "-f"]