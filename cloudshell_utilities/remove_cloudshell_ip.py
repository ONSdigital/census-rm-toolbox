import argparse
import os

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to whitelist a cloudshell IP in a projects RM cluster')
    parser.add_argument('project_id', help='Target project ID', type=str)
    return parser.parse_args()


def main():
    args = parse_arguments()

    service = discovery.build('container', 'v1', credentials=GoogleCredentials.get_application_default())

    request = service.projects().locations().clusters().get(
        name=f'projects/{args.project_id}/locations/europe-west2/clusters/rm-k8s-cluster')
    response = request.execute()

    current_authorised_networks = response['masterAuthorizedNetworksConfig']

    for index, network in enumerate(current_authorised_networks['cidrBlocks']):
        if network['displayName'] == f'{os.getenv("USER")}_cloudshell':
            current_authorised_networks['cidrBlocks'].pop(index)
            break
    else:
        print('Cannot find matching whitelist entry')
        return

    new_authorised_networks = {'update': {'desiredMasterAuthorizedNetworksConfig': current_authorised_networks}}

    update_request = service.projects().locations().clusters().update(name=f'projects/{args.project_id}/locations'
                                                                           f'/europe-west2/clusters/rm-k8s-cluster',
                                                                      body=new_authorised_networks)

    update_request.execute()
    print(f'Successfully removed whitelist entry in {args.project_id}')


if __name__ == '__main__':
    main()
