#!/usr/bin/env python3
'''
Example UDP echo client script
'''

import argparse
import socket


def main():
    '''
    Entry point
    '''
    parser = argparse.ArgumentParser(description="Runs a simple UDP echo client")
    parser.add_argument('-p', "--port", type=int, help="Port to connect to (default: 1337)")
    parser.add_argument('-i', "--host", help="Remote IP address of server", required=True)
    args = parser.parse_args()

    host = args.host
    port = args.port or 1337

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send data
    message = b'This is the message.'
    print(f"Sending message: {message}")
    sock.sendto(message, (host, port))

    # Look for the response
    data, _server = sock.recvfrom(4096)
    print(f"Received: {data}")


if __name__ == "__main__":
    main()
