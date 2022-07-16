FROM python:3.10-slim
ENV PYTHONUNBUFFERED 1

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait

COPY ./src /src
WORKDIR /src

RUN pip install -r requirements.txt --no-cache-dir

CMD /wait && python /src/main.py

