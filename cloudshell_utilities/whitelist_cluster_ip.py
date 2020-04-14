import argparse

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

from remove_cloudshell_ip import remove_cloudshell_whitelist_entries


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to whitelist an IP in a project RM cluster')
    parser.add_argument('project_id', help='Target project ID', type=str)
    parser.add_argument('ip_address', help='IP address to whitelist', type=str)
    parser.add_argument('name', help="Person's name", type=str)
    parser.add_argument('suffix', help="Identifying suffix", type=str)
    return parser.parse_args()


def remove_ip_entries(current_authorised_networks, ips_to_remove):
    ips_to_remove_cidr = []

    for ip in ips_to_remove:
        ips_to_remove_cidr.append(f'{ip}/32')

    authorised_networks = []
    for index, network in enumerate(current_authorised_networks['cidrBlocks']):
        if network['cidrBlock'] not in ips_to_remove_cidr:
            authorised_networks.append(network)
    new_authorised_networks = {
        'update': {
            'desiredMasterAuthorizedNetworksConfig': {
                'enabled': True,
                'cidrBlocks': authorised_networks
            }
        }
    }
    return new_authorised_networks


def unwhitelist_cluster_ips(project_id, ips_to_remove):
    service = discovery.build('container', 'v1', credentials=GoogleCredentials.get_application_default())

    get_current_whitelist_request = service.projects().locations().clusters().get(
        name=f'projects/{project_id}/locations/europe-west2/clusters/rm-k8s-cluster')
    response = get_current_whitelist_request.execute()

    current_authorised_networks = response['masterAuthorizedNetworksConfig']

    new_authorised_networks = remove_ip_entries(current_authorised_networks, ips_to_remove)

    update_request = service.projects().locations().clusters().update(name=f'projects/{project_id}/locations'
                                                                           f'/europe-west2/clusters/rm-k8s-cluster',
                                                                      body=new_authorised_networks)

    update_request.execute()


def whitelist_cluster_ip(project_id, ip_address, suffix, name, ips_to_remove=None):
    service = discovery.build('container', 'v1', credentials=GoogleCredentials.get_application_default())

    get_current_whitelist_request = service.projects().locations().clusters().get(
        name=f'projects/{project_id}/locations/europe-west2/clusters/rm-k8s-cluster')
    response = get_current_whitelist_request.execute()

    current_authorised_networks = response['masterAuthorizedNetworksConfig']

    if ip_address:
        ip_exists = any(elem['cidrBlock'] == f'{ip_address}/32' for elem in current_authorised_networks['cidrBlocks'])

    if not ip_exists:
        if suffix == "_cloudshell":
            print('Removing cloudshell entries for you')
            new_authorised_networks = remove_cloudshell_whitelist_entries(current_authorised_networks)
        elif ips_to_remove:
            new_authorised_networks = remove_ip_entries(ips_to_remove)
        else:
            new_authorised_networks = {
                'update': {
                    'desiredMasterAuthorizedNetworksConfig': {
                        'enabled': True,
                        'cidrBlocks': current_authorised_networks['cidrBlocks']
                    }
                }
            }

        if ip_address:
            new_ip = {'displayName': f'{name}{suffix}',
                      'cidrBlock': f'{ip_address}/32'}

            new_authorised_networks['update']['desiredMasterAuthorizedNetworksConfig']['cidrBlocks'].append(new_ip)

        update_request = service.projects().locations().clusters().update(name=f'projects/{project_id}/locations'
                                                                               f'/europe-west2/clusters/rm-k8s-cluster',
                                                                          body=new_authorised_networks)

        update_request.execute()

        if ip_address:
            print("Successfully Whitelisted IP ")
    else:
        print(f'IP already whitelisted')


def main():
    args = parse_arguments()
    whitelist_cluster_ip(args.project_id, args.ip_address, args.suffix, args.name)


if __name__ == '__main__':
    main()
