import argparse
import json
import os

from whitelist_db_ip import whitelist_db_ip
from whitelist_service_ip import whitelist_service_ip
from add_cluster_ip import whitelist_cluster_ip


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to whitelist for WFH access to services')
    parser.add_argument('project', help='Project', type=str)
    return parser.parse_args()


def main():
    args = parse_arguments()
    project_id = args.project
    os.system('rm whitelist.json')
    os.system('gsutil cp gs://census-rm-whitelist/whitelist.json .')

    with open('whitelist.json', 'r') as whitelist_file:
        whitelist = json.load(whitelist_file)

    for person in whitelist['whitelist']:
        person_name = person['name']
        ip_address = person['ip']

        if person['cluster']:
            whitelist_cluster_ip(project_id, ip_address, ' WFH', person_name)

        if person['database']:
            whitelist_db_ip(ip_address, person_name, project_id)

        for service in person['services']:
            whitelist_service_ip(ip_address, service)

    os.system('rm whitelist.json')


if __name__ == '__main__':
    main()
