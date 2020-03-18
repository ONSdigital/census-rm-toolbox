import argparse
import copy
import json
import os


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to whitelist an IP address in for WFH access')
    parser.add_argument('ip', help='IP Address', type=str)
    parser.add_argument('service', help='Service', type=str)
    return parser.parse_args()


def main():
    args = parse_arguments()
    ip_to_whitelist = f'{args.ip}/32'

    stream = os.popen(f'kubectl get service {args.service} -o json')
    output = stream.read()

    parsed_json = json.loads(output)

    lb_ips = copy.copy(parsed_json['spec']['loadBalancerSourceRanges'])

    if ip_to_whitelist not in lb_ips:
        lb_ips.append(ip_to_whitelist)
        patch_body = {"spec": {"loadBalancerSourceRanges": lb_ips}}
        os.system(f"kubectl patch service -p '{json.dumps(patch_body)}' {args.service}")
        print("IP successfully whitelisted")
    else:
        print("IP already whitelisted")


if __name__ == '__main__':
    main()
