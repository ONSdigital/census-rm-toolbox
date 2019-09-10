FROM python:3.7-slim

ENV RABBITMQ_SERVICE_HOST rabbitmq
ENV RABBITMQ_SERVICE_PORT 5672
ENV RABBITMQ_HTTP_PORT 15672
ENV RABBITMQ_VHOST /
ENV RABBITMQ_USER guest
ENV RABBITMQ_PASSWORD guest

WORKDIR /app
COPY . /app
RUN pip install pipenv
RUN pipenv install --system --deploy

RUN chmod +x /app/splashscreen.sh
RUN echo "/app/splashscreen.sh" >> /root/.bashrc