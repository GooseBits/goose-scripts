#!/usr/bin/env python3
'''
Example TCP echo server script.
'''

import argparse
import socket


def main():
    '''
    Entry point
    '''
    parser = argparse.ArgumentParser(description="Runs a simple TCP echo server")
    parser.add_argument('-p', "--port", type=int, help="Port to run on (default: 1337)")
    parser.add_argument('-i', "--bind-ip", help="Local IP address to bind to. (default: 0.0.0.0)")
    args = parser.parse_args()

    host = args.bind_ip or "0.0.0.0"
    port = args.port or 1337

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = (host, port)
    print(f"Starting up on {host} port {port}")
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)

    while True:
        # Wait for a connection
        print("Waiting for connections")
        connection, client_address = sock.accept()

        try:
            print(f"Connection from {client_address}")

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(16)
                print(f"Received: {data}")
                if data:
                    print("Echoing data back to the client")
                    connection.sendall(data)
                else:
                    print(f"No more data from {client_address}")
                    break
        finally:
            # Clean up the connection
            connection.close()


if __name__ == "__main__":
    main()
