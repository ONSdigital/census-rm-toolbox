#!/usr/bin/env bash

if [ -z "$IMAGE" ]; then
   IMAGE=eu.gcr.io/census-rm-ci/census-rm-toolbox:latest
fi

echo "Image $IMAGE"

kubectl run toolbox -it --rm \
   --generator=run-pod/v1 \
   --image $IMAGE\
   --env=RABBITMQ_USER=$(kubectl get secret rabbitmq -o=jsonpath="{.data.rabbitmq-username}" | base64 --decode) \
   --env=RABBITMQ_PASSWORD=$(kubectl get secret rabbitmq -o=jsonpath="{.data.rabbitmq-password}" | base64 --decode) \
   --env=RABBITMQ_SERVICE_HOST=rabbitmq \
   --env=RABBITMQ_SERVICE_PORT=5672 \
   --env=RABBITMQ_HTTP_PORT=15672 \
   --env=RABBITMQ_VHOST='/' \
   -- /bin/bash