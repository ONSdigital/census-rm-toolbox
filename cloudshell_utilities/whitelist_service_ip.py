import argparse
import json
import os


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to whitelist an IP address for WFH access to services')
    parser.add_argument('ip', help='IP Address', type=str)
    parser.add_argument('service', help='Service', type=str)
    return parser.parse_args()


def unwhitelist_service_ips(ips_to_remove, service):
    ips_to_remove_cidr = []

    for ip in ips_to_remove:
        ips_to_remove_cidr.append(f'{ip}/32')

    stream = os.popen(f'kubectl get service {service} -o json')
    output = stream.read()

    parsed_json = json.loads(output)

    new_lb_ips = []
    current_lb_ips = parsed_json['spec']['loadBalancerSourceRanges']

    for current_lb_ip in current_lb_ips:
        if current_lb_ip not in ips_to_remove_cidr:
            new_lb_ips.append(current_lb_ip)

    patch_body = {"spec": {"loadBalancerSourceRanges": new_lb_ips}}
    os.system(f"kubectl patch service -p '{json.dumps(patch_body)}' {service}")


def whitelist_service_ip(ip, service):
    ip_to_whitelist = f'{ip}/32'

    stream = os.popen(f'kubectl get service {service} -o json')
    output = stream.read()

    parsed_json = json.loads(output)

    lb_ips = parsed_json['spec']['loadBalancerSourceRanges']

    if ip_to_whitelist not in lb_ips:
        lb_ips.append(ip_to_whitelist)
        patch_body = {"spec": {"loadBalancerSourceRanges": lb_ips}}
        os.system(f"kubectl patch service -p '{json.dumps(patch_body)}' {service}")
        print("IP successfully whitelisted")
    else:
        print("IP already whitelisted")


def main():
    args = parse_arguments()
    whitelist_service_ip(args.ip, args.service)


if __name__ == '__main__':
    main()
