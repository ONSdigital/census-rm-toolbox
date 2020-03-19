import argparse
import json
import os

import requests


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to whitelist an IP address for WFH access to DB')
    parser.add_argument('ip', help='IP Address', type=str)
    parser.add_argument('name', help="Person's Name", type=str)
    parser.add_argument('project', help='Project', type=str)
    return parser.parse_args()


def whitelist_ip(new_ip, new_name, project):
    stream = os.popen('gcloud auth print-access-token')
    access_token = str(stream.read())
    access_token = access_token.replace('\n', '')

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"https://www.googleapis.com/sql/v1beta4/projects/{project}/instances",
                            headers=headers)
    response.raise_for_status()

    for item in response.json()['items']:
        authorized_networks = item['settings']['ipConfiguration']['authorizedNetworks']

        ip_exists = any(elem['value'] == new_ip for elem in authorized_networks)

        if not ip_exists:
            authorized_networks.append({'value': new_ip, 'name': new_name, 'kind': 'sql#aclEntry'})
            patch_data = json.dumps({'settings': {'ipConfiguration': {'authorizedNetworks': authorized_networks}}})
            response = requests.patch(f"https://www.googleapis.com/sql/v1beta4/projects/{project}/instances/{item['name']}",
                                      patch_data, headers=headers)
            response.raise_for_status()
            print(f'IP successfully whitelisted')
        else:
            print(f'IP already whitelisted')


def main():
    args = parse_arguments()
    whitelist_ip(f'{args.ip}/32', f'{args.name} WFH', args.project)


if __name__ == '__main__':
    main()
