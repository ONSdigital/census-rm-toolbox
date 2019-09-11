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
        queue_name = queue['name']
        queue_details = requests.get(
            f'http://{Config.RABBITMQ_HOST}:{Config.RABBITMQ_HTTP_PORT}/api/queues/{v_host}/{queue_name}',
            auth=HTTPBasicAuth(Config.RABBITMQ_USER, Config.RABBITMQ_PASSWORD)).json()

        try:
            redeliver_rate = queue_details['message_stats']['redeliver_details']['rate']
            publish_rate = queue_details['message_stats']['publish_details']['rate']
            ack_rate = queue_details['message_stats']['ack_details']['rate']

            json_to_log = {
                "queue_name": queue_name,
                "redeliver_rate": redeliver_rate,
                "publish_rate": publish_rate,
                "ack_rate": ack_rate
            }
            print(json.dumps(json_to_log))
        except KeyError:
            pass


if __name__ == "__main__":
    main()
