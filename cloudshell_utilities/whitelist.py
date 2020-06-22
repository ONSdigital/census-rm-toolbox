import argparse
import json

from cloudshell_utilities.whitelist_cluster_ip import whitelist_cluster_list
from cloudshell_utilities.whitelist_db_ip import whitelist_db_list
from cloudshell_utilities.whitelist_service_ip import whitelist_service_ip_list


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to whitelist for WFH access to services')
    parser.add_argument('project', help='Project', type=str)
    parser.add_argument('config', help='Project', type=str)
    return parser.parse_args()


def whitelist(project_id, config_file_name):
    with open(config_file_name, 'r') as whitelist_file:
        whitelist = json.load(whitelist_file)

    cluster_whitelist = []
    db_whitelist = []
    for person in whitelist:
        if person['cluster']:
            cluster_whitelist.append(person)

        if person['database']:
            db_whitelist.append(person)

    services = set()
    for person in whitelist:
        for service in person['services']:
            services.add(service)

    whitelist_cluster_list(project_id, cluster_whitelist)
    whitelist_db_list(db_whitelist, project_id)

    for service in services:
        ip_list = []

        for person in whitelist:
            for person_service in person['services']:
                if person_service == service:
                    ip_list.append(person['ip'])

        whitelist_service_ip_list(ip_list, service)


def main():
    args = parse_arguments()
    whitelist(args.project, args.config)


if __name__ == '__main__':
    main()
