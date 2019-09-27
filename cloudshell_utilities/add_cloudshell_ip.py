import argparse
import os

from googleapiclient import discovery
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
from retrying import retry


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to whitelist a cloudshell IP in a projects RM cluster')
    parser.add_argument('project_id', help='Target project ID', type=str)
    parser.add_argument('ip_address', help='IP address to whitelist', type=str)
    return parser.parse_args()


def retry_if_http_error(exception):
    return isinstance(exception, HttpError)


@retry(retry_on_exception=retry_if_http_error, wait_exponential_multiplier=1000, wait_exponential_max=10000,
       stop_max_attempt_number=10)
def execute_request(request):
    response = request.execute()
    return response


def main():
    args = parse_arguments()

    service = discovery.build('container', 'v1', credentials=GoogleCredentials.get_application_default())

    request = service.projects().locations().clusters().get(
        name=f'projects/{args.project_id}/locations/europe-west2/clusters/rm-k8s-cluster')
    response = execute_request(request)

    current_authorised_networks = response['masterAuthorizedNetworksConfig']
    new_ip = {'displayName': f'{os.getenv("USER")}_cloudshell',
              'cidrBlock': f'{args.ip_address}/32'}

    new_authorised_networks = {'update': {'desiredMasterAuthorizedNetworksConfig': current_authorised_networks}}

    new_authorised_networks['update']['desiredMasterAuthorizedNetworksConfig']['cidrBlocks'].append(new_ip)

    update_request = service.projects().locations().clusters().update(name=f'projects/{args.project_id}/locations'
                                                                           f'/europe-west2/clusters/rm-k8s-cluster',
                                                                      body=new_authorised_networks)

    execute_request(update_request)
    print("Successfully Whitelisted IP ")


if __name__ == '__main__':
    main()
