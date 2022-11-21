#!/usr/bin/env python3
'''
Basic WebSocket client example
'''

import asyncio
import argparse
import websockets


async def hello(uri):
    '''
    Say hello
    '''
    async with websockets.connect(uri) as websocket:
        name = input("What's your name? ")

        await websocket.send(name)
        print(f"> {name}")

        greeting = await websocket.recv()
        print(f"< {greeting}")


def main():
    '''
    Entry point
    '''
    parser = argparse.ArgumentParser(description="Runs a simple WebSocket client")
    parser.add_argument(
        '-u', "--uri", action="store", required=True, help="WebSocket URI to connect to (ex: ws://<ip>:<port>).")
    args = parser.parse_args()

    asyncio.get_event_loop().run_until_complete(hello(args.uri))


if __name__ == "__main__":
    main()
