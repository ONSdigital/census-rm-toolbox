FROM python:3.7-slim

ENV RABBITMQ_SERVICE_HOST rabbitmq
ENV RABBITMQ_SERVICE_PORT 5672
ENV RABBITMQ_HTTP_PORT 15672
ENV RABBITMQ_VHOST /
ENV RABBITMQ_USER guest
ENV RABBITMQ_PASSWORD guest

RUN apt-get update
RUN apt-get -yq install curl
RUN apt-get -yq install jq
RUN apt-get -yq install vim-tiny
RUN apt-get -yq install postgresql-client || true
RUN apt-get -yq clean

WORKDIR /app
COPY . /app
RUN pip install pipenv
RUN pipenv install --system --deploy

RUN chmod +x /app/splashscreen.sh
RUN chmod +x /app/watch_for_poison_messages.sh
RUN chmod +x /app/aliases.sh
RUN chmod +x /app/watch_for_slow_event_processing.sh
RUN echo "source /app/aliases.sh" >> /root/.bashrc
RUN echo "/app/splashscreen.sh" >> /root/.bashrc