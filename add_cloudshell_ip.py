import argparse
import os

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
    new_ip = {'displayName': f'{os.getenv("USER")}_cloudshell',
              'cidrBlock': f'{args.ip_address}/32'}

    new_authorised_networks = {'update': {'desiredMasterAuthorizedNetworksConfig': current_authorised_networks}}

    new_authorised_networks['update']['desiredMasterAuthorizedNetworksConfig']['cidrBlocks'].append(new_ip)

    update_request = service.projects().locations().clusters().update(name=f'projects/{args.project_id}/locations'
                                                                           f'/europe-west2/clusters/rm-k8s-cluster',
                                                                      body=new_authorised_networks)

    update_request.execute()


if __name__ == '__main__':
    main()
