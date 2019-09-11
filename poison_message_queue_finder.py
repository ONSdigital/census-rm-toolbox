import json
import urllib.parse

import requests
from requests.auth import HTTPBasicAuth

from config import Config


def main():
    v_host = urllib.parse.quote(Config.RABBITMQ_VHOST, safe='')

    response = requests.get(f"http://{Config.RABBITMQ_HOST}:{Config.RABBITMQ_HTTP_PORT}/api/queues/",
                            auth=HTTPBasicAuth(Config.RABBITMQ_USER, Config.RABBITMQ_PASSWORD))

    all_queues = response.json()

    for queue in all_queues:
        try:
            queue_name = queue['name']
        except [TypeError, KeyError]:
            print(f'Unexpected data for queue: {queue}')
            pass

        queue_details = requests.get(
            f'http://{Config.RABBITMQ_HOST}:{Config.RABBITMQ_HTTP_PORT}/api/queues/{v_host}/{queue_name}',
            auth=HTTPBasicAuth(Config.RABBITMQ_USER, Config.RABBITMQ_PASSWORD)).json()

        redeliver_rate = 0
        publish_rate = 0
        ack_rate = 0

        try:
            redeliver_rate = queue_details['message_stats']['redeliver_details']['rate']
        except KeyError:
            pass

        try:
            publish_rate = queue_details['message_stats']['publish_details']['rate']
        except KeyError:
            pass

        try:
            ack_rate = queue_details['message_stats']['ack_details']['rate']
        except KeyError:
            pass

        json_to_log = {
            "queue_name": queue_name,
            "redeliver_rate": redeliver_rate,
            "publish_rate": publish_rate,
            "ack_rate": ack_rate
        }
        print(json.dumps(json_to_log))


if __name__ == "__main__":
    main()
