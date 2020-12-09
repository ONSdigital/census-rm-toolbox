FROM python:3.7-slim

RUN pip install pipenv

COPY .bashrc_extras /tmp

RUN apt-get update && apt-get -yq install curl && apt-get -yq install jq && apt-get -yq install vim-tiny && \
    apt-get -yq install unzip && apt-get -yq install postgresql-client || true && \
    apt-get -yq install openssh-client || true && apt-get -yq install procps || true && \
    apt-get -yq clean && groupadd --gid 1000 toolbox && \
    useradd --create-home --system --uid 1000 --gid toolbox toolbox && \
    cat /tmp/.bashrc_extras >> /home/toolbox/.bashrc && rm /tmp/.bashrc_extras
WORKDIR /home/toolbox

ENV RABBITMQ_SERVICE_HOST rabbitmq
ENV RABBITMQ_SERVICE_PORT 5672
ENV RABBITMQ_HTTP_PORT 15672
ENV RABBITMQ_VHOST /
ENV RABBITMQ_USER guest
ENV RABBITMQ_PASSWORD guest

COPY Pipfile* /home/toolbox/
RUN pipenv install --system --deploy
USER toolbox

RUN mkdir /home/toolbox/.postgresql &&  mkdir /home/toolbox/.postgresql-rw &&  mkdir /home/toolbox/.postgresql-action

COPY --chown=toolbox . /home/toolbox