FROM python:3.7-slim

RUN pip install pipenv

RUN apt-get update && apt-get -yq install curl && apt-get -yq install jq && apt-get -yq install vim-tiny && \
    apt-get -yq install postgresql-client || true && apt-get -yq install openssh-client || true && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    apt-get -yq install apt-transport-https ca-certificates gnupg && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && apt-get -yq install google-cloud-sdk && \
    apt-get -yq install kubectl && \
    apt-get -yq clean && groupadd --gid 1000 toolbox && \
    useradd --create-home --system --uid 1000 --gid toolbox toolbox && \
    echo "source /home/toolbox/aliases.sh" >> /home/toolbox/.bashrc && \
    echo "/home/toolbox/splashscreen.sh" >> /home/toolbox/.bashrc && \
    echo 'PS1="[$PROJECT_NAME]-TOOLZ🔥> "' >> /home/toolbox/.bashrc && \
    echo "export PATH=/home/toolbox:$PATH" >> /home/toolbox/.bashrc
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