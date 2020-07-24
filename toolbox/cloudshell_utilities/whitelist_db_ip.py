import argparse
import json
import os

import requests

GOOGLE_API_SQL_PROJECTS = 'https://www.googleapis.com/sql/v1beta4/projects'


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to whitelist an IP address for WFH access to DB')
    parser.add_argument('ip', help='IP Address', type=str)
    parser.add_argument('name', help="Person's Name", type=str)
    parser.add_argument('project', help='Project', type=str)
    return parser.parse_args()


def whitelist_db_ip(new_ip, new_name, project):
    stream = os.popen('gcloud auth print-access-token')
    access_token = str(stream.read())
    access_token = access_token.replace('\n', '')

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{GOOGLE_API_SQL_PROJECTS}/{project}/instances",
                            headers=headers)
    response.raise_for_status()

    for item in response.json()['items']:
        authorized_networks = item['settings']['ipConfiguration']['authorizedNetworks']

        ip_exists = any(elem['value'] == new_ip for elem in authorized_networks)

        if not ip_exists:
            authorized_networks.append({'value': new_ip, 'name': new_name, 'kind': 'sql#aclEntry'})
            patch_data = json.dumps({'settings': {'ipConfiguration': {'authorizedNetworks': authorized_networks}}})
            response = requests.patch(f"{GOOGLE_API_SQL_PROJECTS}/{project}/instances/{item['name']}", patch_data,
                                      headers=headers)
            response.raise_for_status()
            print('IP successfully whitelisted')
        else:
            print('IP already whitelisted')


def whitelist_db_list(whitelist, project):
    authorized_networks = []

    for item in whitelist:
        authorized_networks.append({'value': f"{item['ip']}/32", 'name': item['name'], 'kind': 'sql#aclEntry'})

    stream = os.popen('gcloud auth print-access-token')
    access_token = str(stream.read())
    access_token = access_token.replace('\n', '')

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{GOOGLE_API_SQL_PROJECTS}/{project}/instances",
                            headers=headers)
    response.raise_for_status()

    for item in response.json()['items']:
        patch_data = json.dumps({'settings': {'ipConfiguration': {'authorizedNetworks': authorized_networks}}})
        response = requests.patch(f"{GOOGLE_API_SQL_PROJECTS}/{project}/instances/{item['name']}", patch_data,
                                  headers=headers)
        response.raise_for_status()


def main():
    args = parse_arguments()
    whitelist_db_ip(f'{args.ip}/32', f'{args.name} WFH', args.project)


if __name__ == '__main__':
    main()
