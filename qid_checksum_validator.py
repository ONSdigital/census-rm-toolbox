import argparse
import os
from typing import Tuple


def validate(code: str, modulus: int, factor: int) -> Tuple[bool, str]:
    code_component = code[:-2]
    actual_checksum_digits = code[-2:]
    valid_checksum_digits = str(generate_checksum_digits(code_component, modulus, factor)).zfill(2)
    return actual_checksum_digits == valid_checksum_digits, valid_checksum_digits


def generate_checksum_digits(code: str, modulus: int, factor: int) -> int:
    remainder = ord(code[0])
    for char in code[1:]:
        ascii_value = ord(char)
        remainder = ((remainder * factor) + ascii_value) % modulus
    return remainder % modulus


def find_nearby_valid_qids(code: str, modulus: int, factor: int):
    nearby_qids = []
    code_component = code[:-2]
    actual_checksum_digits = code[-2:]
    for index, char in reversed(list(enumerate(code_component))):
        for attempt_value in range(ord('0'), ord('9') + 1):
            nearby_code = code_component[:index] + chr(attempt_value) + code_component[index + 1:]
            attempt_checksum = generate_checksum_digits(nearby_code, modulus, factor)
            if str(attempt_checksum).zfill(2) == actual_checksum_digits:
                nearby_qids.append((nearby_code + actual_checksum_digits, index))
    return nearby_qids


def show_nearby_valid_qids(code: str, modulus: int, factor: int):
    nearby_qids = find_nearby_valid_qids(code, modulus, factor)
    if nearby_qids:
        for nearby_qid, replaced_index in nearby_qids:
            position_indicator = (replaced_index * ' ') + '^'
            print(f'Found a nearby valid QID by changing one digit: {nearby_qid}')
            print(f'                                                {position_indicator}')


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Validate the checksum of a code')
    parser.add_argument('code', help='Code including checksum to validate', type=str)
    parser.add_argument('--modulus', help='Modulus for checksum algorithm',
                        type=int, default=os.getenv('QID_MODULUS'), required=True)
    parser.add_argument('--factor', help='Factor for checksum algorithm',
                        type=int, default=os.getenv('QID_FACTOR'), required=True)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    is_valid, valid_checksum = validate(args.code, args.modulus, args.factor)
    if is_valid:
        print(f'{args.code} is valid! ✅')
    else:
        print(f'{args.code} is NOT valid ❌')
        print(f'The valid checksum digits for this QID component would be {valid_checksum}')
        show_nearby_valid_qids(args.code, args.modulus, args.factor)
        exit(1)
