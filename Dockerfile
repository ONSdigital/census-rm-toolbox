FROM python:3.7-slim

RUN pip install pipenv

COPY .bashrc_extras /tmp

RUN apt-get update && apt-get -yq install curl && apt-get -yq install jq && apt-get -yq install vim-tiny && \
    apt-get -yq install unzip && apt-get -yq install postgresql-client || true && \
    apt-get -yq install openssh-client || true && apt-get -yq install procps || true && \
    apt-get -yq install apt-transport-https ca-certificates gnupg && \
    apt-get -yq clean && apt-get -yq install cron && apt-get -yq install sudo && groupadd --gid 1000 toolbox && \
    useradd --create-home --system --uid 1000 --gid toolbox toolbox && \
    usermod -a -G sudo toolbox && echo "toolbox ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    cat /tmp/.bashrc_extras >> /home/toolbox/.bashrc && rm /tmp/.bashrc_extras

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
    | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && \
    apt-get update -y && apt-get install google-cloud-sdk -y

COPY toolboxjob /etc/cron.d/toolboxjob

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

CMD ["sudo", "cron", "-f"]