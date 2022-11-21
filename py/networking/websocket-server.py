#!/usr/bin/env python3
'''
Basic WebSocket server example
'''

import asyncio
import argparse
import websockets


async def hello(websocket, _path):
    '''
    Handle hello
    '''
    name = await websocket.recv()
    print(f"< {name}")

    greeting = f"Hello {name}!"

    await websocket.send(greeting)
    print(f"> {greeting}")


def main():
    '''
    Entry point
    '''
    parser = argparse.ArgumentParser(description="Runs a simple WebSocket server")
    parser.add_argument('-p', "--port", type=int, help="Port to run on (default: 1337)")
    parser.add_argument('-i', "--bind-ip", help="Local IP address to bind to. (default: 0.0.0.0)")
    args = parser.parse_args()

    host = args.bind_ip or "0.0.0.0"
    port = args.port or 1337

    start_server = websockets.serve(hello, host, port)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
