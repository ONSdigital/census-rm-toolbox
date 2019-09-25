"""
BEFORE RUNNING:
---------------
1. If not already done, enable the Kubernetes Engine API
   and check the quota for your project at
   https://console.developers.google.com/apis/api/container
2. This sample uses Application Default Credentials for authentication.
   If not already done, install the gcloud CLI from
   https://cloud.google.com/sdk and run
   `gcloud beta auth application-default login`.
   For more information, see
   https://developers.google.com/identity/protocols/application-default-credentials
3. Install the Python client library for Google APIs by running
   `pip install --upgrade google-api-python-client`
"""
import argparse
import os
from pprint import pprint

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to whitelist a cloudshell IP in a projects RM cluster')
    parser.add_argument('project_id', help='Target project ID', type=str)
    parser.add_argument('ip_address', help='IP address to whitelist', type=str)
    return parser.parse_args()


def main():
    args = parse_arguments()
    credentials = GoogleCredentials.get_application_default()

    service = discovery.build('container', 'v1', credentials=credentials)

    request = service.projects().locations().clusters().get(
        name=f'projects/{args.project_id}/locations/europe-west2/clusters/rm-k8s-cluster')
    response = request.execute()

    current_authorised_networks = response['masterAuthorizedNetworksConfig']

    for index, network in enumerate(current_authorised_networks['cidrBlocks']):
        if network['displayName'] == f'{os.getenv("USER")}_cloudshell':
            current_authorised_networks['cidrBlocks'].pop(index)
            break
    else:
        print('Cannot matching whitelist entry')


    new_authorised_networks = {'update': {'desiredMasterAuthorizedNetworksConfig': current_authorised_networks}}

    update_request = service.projects().locations().clusters().update(name=f'projects/{args.project_id}/locations'
                                                                           f'/europe-west2/clusters/rm-k8s-cluster',
                                                                      body=new_authorised_networks)

    update_request.execute()


if __name__ == '__main__':
    main()
