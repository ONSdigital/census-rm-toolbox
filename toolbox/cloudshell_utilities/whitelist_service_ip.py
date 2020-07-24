import argparse
import json
import os


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to whitelist an IP address for WFH access to services')
    parser.add_argument('ip', help='IP Address', type=str)
    parser.add_argument('service', help='Service', type=str)
    return parser.parse_args()


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


def whitelist_service_ip_list(ip_list, service):
    lb_ips = []

    for ip in ip_list:
        ip_to_whitelist = f'{ip}/32'
        lb_ips.append(ip_to_whitelist)

    patch_body = {"spec": {"loadBalancerSourceRanges": lb_ips}}
    os.system(f"kubectl patch service -p '{json.dumps(patch_body)}' {service}")


def main():
    args = parse_arguments()
    whitelist_service_ip(args.ip, args.service)


if __name__ == '__main__':
    main()
