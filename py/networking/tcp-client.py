#!/usr/bin/env python3
'''
Example TCP echo client script
'''

import argparse
import socket


def main():
    '''
    Entry point
    '''
    parser = argparse.ArgumentParser(description="Runs a simple TCP echo client")
    parser.add_argument('-p', "--port", type=int, help="Port to connect to (default: 1337)")
    parser.add_argument('-i', "--host", help="Remote IP address of server", required=True)
    args = parser.parse_args()

    host = args.host
    port = args.port or 1337

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    sock.connect((host, port))

    try:
        # Send data
        message = b'This is the message.'
        print(f"Sending message: {message}")
        sock.sendall(message)

        # Look for the response
        amount_received = 0
        amount_expected = len(message)

        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            print(f"Received: {data}")

    finally:
        print("Closing socket")
        sock.close()


if __name__ == "__main__":
    main()
