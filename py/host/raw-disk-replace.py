#!/usr/bin/env python3
'''
NOTE: We launch with Python 3 by default, but this script WILL work on anything from
Python 2.7 and up.
'''

import argparse
import os
import sys


def replace_targets(path, search, replace, block_size=5242880):
    '''
    NOTE:
    Modes 'r+', 'w+' and 'a+' open the file for updating (reading and writing); note that 'w+' truncates the file.
    Append 'b' to the mode to open the file in binary mode, on systems that differentiate between binary and text files;
    on systems that don't have this distinction, adding the 'b' has no effect.
    '''
    with open(path, "r+b") as f:
        # Get the total size of the file
        file_size = os.stat(path).st_size

        while True:
            offset = f.tell()
            buffer = f.read(block_size)

            # Find all occurrences in this chunk
            pos = -1
            while True:
                pos = buffer.find(search, pos + 1)
                if pos == -1:
                    break

                f.seek(offset + pos)
                f.write(replace)
                f.flush()

            # Check if we're at the end of the file
            next_block = offset + block_size
            if next_block >= file_size:
                break

            # Move on to the next chunk, overlapping enough for the search size
            f.seek(next_block - len(search) + 1)


def main():
    '''
    Entry point
    '''
    #
    # Works for anything from Python 2.7 through 3.7
    #
    parser = argparse.ArgumentParser("Replacer", description="Replace stuff")
    parser.add_argument(
        "-p", "--path", help="File to use (i.e. /dev/sda1)", required=True)
    parser.add_argument(
        "-s", "--search", help="Bytes to search for (i.e. '\\xDE\\xAD\\xBE\\xEF' or 'whatever')", required=True)
    parser.add_argument(
        "-r", "--replace", help="Replace with these bytes (must be same length as --search).", required=True)
    parser.add_argument(
        "-b", "--block-size", help="Block size for reading the file (default=5242880)", type=int, default=5242880)
    args = parser.parse_args()

    if not os.path.exists(args.path) or not os.path.isfile(args.path):
        sys.exit(1)

    if len(args.search) != len(args.replace):
        sys.exit(2)

    search = args.search
    replace = args.replace

    if sys.version_info >= (3, 0):
        search = bytes([ord(i) for i in args.search])
        replace = bytes([ord(i) for i in args.replace])

    replace_targets(args.path, search, replace, block_size=args.block_size)


if __name__ == "__main__":
    main()
