#!/usr/bin/env python3
'''
Example UDP echo server script.
'''

import argparse
import socket


def main():
    '''
    Entry point
    '''
    parser = argparse.ArgumentParser(description="Runs a simple UDP echo server")
    parser.add_argument('-p', "--port", type=int, help="Port to run on (default: 1337)")
    parser.add_argument('-i', "--bind-ip", help="Local IP address to bind to. (default: 0.0.0.0)")
    args = parser.parse_args()

    host = args.bind_ip or "0.0.0.0"
    port = args.port or 1337

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = (host, port)
    print(f"Starting up on {host} port {port}")
    sock.bind(server_address)

    while True:
        # Wait for a connection
        data, address = sock.recvfrom(4096)
        print(f"Recieved: {data}")

        if data:
            sent = sock.sendto(data, address)
            print(f"Send {sent} bytes back to {address}")


if __name__ == "__main__":
    main()
