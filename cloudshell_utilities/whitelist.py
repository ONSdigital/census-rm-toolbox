import argparse
import json
import time

from whitelist_db_ip import whitelist_db_ip, unwhitelist_db_ips
from whitelist_service_ip import whitelist_service_ip, unwhitelist_service_ips
from whitelist_cluster_ip import whitelist_cluster_ip, unwhitelist_cluster_ips


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to whitelist for WFH access to services')
    parser.add_argument('project', help='Project', type=str)
    return parser.parse_args()


def unwhitelist(project_id):
    with open(f'census-rm-whitelist/{project_id}/previous_whitelist.json', 'r') as whitelist_file:
        previous_whitelist = json.load(whitelist_file)

    previous_ips = []
    previous_services = set()
    for person in previous_whitelist['whitelist']:
        previous_ips.append(person['ip'])

        for service in person['services']:
            previous_services.add(service)

    unwhitelist_cluster_ips(project_id, previous_ips)
    unwhitelist_db_ips(previous_ips, project_id)
    for service in previous_services:
        unwhitelist_service_ips(previous_ips, service)


def whitelist(project_id):
    with open(f'census-rm-whitelist/{project_id}/current_whitelist.json', 'r') as whitelist_file:
        current_whitelist = json.load(whitelist_file)

    for person in current_whitelist['whitelist']:
        person_name = person['name']
        ip_address = person['ip']

        if person['cluster']:
            whitelist_cluster_ip(project_id, ip_address, ' WFH', person_name)

        if person['database']:
            whitelist_db_ip(ip_address, person_name, project_id)

        for service in person['services']:
            whitelist_service_ip(ip_address, service)


def main():
    args = parse_arguments()
    project_id = args.project
    unwhitelist(project_id)

    # We have to wait until the DB has finished updating otherwise we get a 409 error
    time.sleep(30)

    whitelist(project_id)


if __name__ == '__main__':
    main()
