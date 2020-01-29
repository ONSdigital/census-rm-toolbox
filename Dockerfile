FROM python:3.7-slim

RUN pip install pipenv

RUN apt-get update && apt-get -yq install curl && apt-get -yq install jq && apt-get -yq install vim-tiny && \
    apt-get -yq install postgresql-client || true && apt-get -yq install openssh-client || true && \
    apt-get -yq clean && groupadd --gid 1000 toolbox && \
    useradd --create-home --system --uid 1000 --gid toolbox toolbox && \
    echo "source /app/aliases.sh" >> /home/toolbox/.bashrc && echo "/app/splashscreen.sh" >> /home/toolbox/.bashrc && \
    echo 'PS1="[$PROJECT_NAME]-TOOLZ🔥> "' >> /home/toolbox/.bashrc && \
    echo "export PATH=/app:$PATH" >> /home/toolbox/.bashrc
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

COPY --chown=toolbox . /home/toolbox
