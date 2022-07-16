FROM python:3.8

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait

RUN apt-get update && apt-get install nano

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY /src /app/
COPY prod_ep.sh/ /app/
COPY debug_ep.sh/ /app/
COPY debug_ep.sh/ /app/

EXPOSE 5000 50051

RUN ["chmod", "+x", "prod_ep.sh"]
RUN ["chmod", "+x", "debug_ep.sh"]

CMD  ./prod_ep.sh