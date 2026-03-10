#!/usr/bin/env python3

import argparse
import cowsay

def main():
    parser = argparse.ArgumentParser(description='Two cows say things.')
    parser.add_argument('message1', help='First message')
    parser.add_argument('message2', help='Second message')
    parser.add_argument('-E', '--eyes2', default='oo', help='Eyes of the second cow')
    parser.add_argument('-F', '--cowfile2', default='default', help='Cow type for second cow')
    parser.add_argument('-N', '--tongue2', default='  ', help='Tongue of the second cow')
    args = parser.parse_args()

    cow1_lines = cowsay.cowsay(args.message1).splitlines()
    cow2_lines = cowsay.cowsay(
        args.message2,
        cow=args.cowfile2,
        eyes=args.eyes2,
        tongue=args.tongue2
    ).splitlines()

    h1, h2 = len(cow1_lines), len(cow2_lines)
    max_h = max(h1, h2)

    if h1 < max_h:
        cow1_lines = [''] * (max_h - h1) + cow1_lines
    if h2 < max_h:
        cow2_lines = [''] * (max_h - h2) + cow2_lines

    max_left_width = max(len(line) for line in cow1_lines)

    for left, right in zip(cow1_lines, cow2_lines):
        print(left.ljust(max_left_width) + '    ' + right)

if __name__ == '__main__':
    main()
