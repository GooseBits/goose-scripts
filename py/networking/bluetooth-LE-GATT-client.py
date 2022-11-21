#!/usr/bin/env python3
'''
Example client for Bluetooth Low Energy (LE) devices
'''

import os
import sys
import time
import asyncio
import argparse
import traceback
from bleak import BleakClient
from bleak import discover
from bleak.exc import BleakError


# Populated by parsing services
NOTIFICATION_UUIDS = {}
NOTIF_LOOKUP = {}


def notification_handler(sender, data):
    '''
    Simple notification handler which prints the data received.
    '''
    service_desc = NOTIF_LOOKUP.get(sender, "Unknown Service")
    fmt_data = " ".join("%02x".upper() % b for b in data)
    print(f"{service_desc}: {fmt_data}")


async def parse_services(client):
    '''
    Dump all services, characteristics, and info
    '''
    for service in client.services:
        print(f"\n[Service] {service.uuid}: {service.description}")
        for char in service.characteristics:
            if "read" in char.properties:
                try:
                    value = bytes(await client.read_gatt_char(char.uuid))
                except Exception as e:  # pylint: disable=broad-except
                    value = str(e).encode()
            else:
                value = None

            if "notify" in char.properties:
                # This is something we can recieve notifications about.
                if service.uuid not in NOTIFICATION_UUIDS:
                    NOTIFICATION_UUIDS[service.uuid] = {
                        "service_description": service.description,
                        "notifications": []
                    }

                NOTIF_LOOKUP[char.uuid] = service.description
                NOTIFICATION_UUIDS[service.uuid]["notifications"].append(char.uuid)

            print(f"\t[Char] {char.uuid}: ({','.join(char.properties)}) | Name: {char.description}, Value: {value}")

            for descriptor in char.descriptors:
                value = await client.read_gatt_descriptor(descriptor.handle)
                print(f"\t\t[Descriptor] {descriptor.uuid}: (Handle: {descriptor.handle}) | Value: {bytes(value)} ")

    print("")  # Add a newline for easy readin'


async def scan():
    '''
    Scan for Blutooth LE devices
    '''
    devices = await discover()
    for d in devices:
        print("Found device: ", d.name)
        print("\tAddress: ", d.address)
        print("\tDetails: ", d.details)
        print("\tMetadata: ", d.metadata)

    return devices


async def run_client(address, loop, timeout=10):
    '''
    Connect to a chosen device
    '''
    print("Connecting...")

    async with BleakClient(address, loop=loop, timeout=timeout) as client:
        is_connected = await client.is_connected()
        if not is_connected:
            print("Failed to connect")
            return False

        print("Connected! Parsing services...")

        await parse_services(client)

        for val in NOTIFICATION_UUIDS.values():
            print(f"Enabling notifications for service {val['service_description']}")
            for notif in val["notifications"]:
                try:
                    await client.start_notify(notif, notification_handler)
                except AttributeError:
                    print(f"Could not enable notifications for {notif}")
                    continue

        try:
            # Run the main loop
            print("Listening for notifications. Cntrl-C to exit...")
            while 1:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Clean exit...")
        except Exception as e:  # pylint: disable=broad-except
            print(f"Unhandled exception {e}")

        print("Stopping notifications. Please wait (don't hit cntrl-c again dummy, we're working on it)...")

        for key in NOTIF_LOOKUP.keys():  #: pylint: disable=consider-iterating-dictionary
            await client.stop_notify(key)

    return True


def main(timeout=10):
    '''
    Entry point
    '''
    os.system("clear")

    # Look for compatible devices
    loop = asyncio.get_event_loop()

    while 1:
        print("Looking for compatible devices...")

        devices = loop.run_until_complete(scan())

        print("\nChoose your device:")
        print("\t0. Rescan")
        for idx, d in enumerate(devices):
            choice = idx + 1
            print(f"\t{choice}. {d.name}")

        choice = input("\nWhich device? ")
        try:
            choice = int(choice)

            if choice > len(devices) or choice < 0:
                raise ValueError("no")
        except ValueError:
            print("Invalid. You're bad at computers.")
            sys.exit(1)

        if choice == 0:
            os.system("clear")
            continue
        break

    choice = devices[choice - 1]
    print(f"Choice: {choice.name}")

    address = choice.address
    success = loop.run_until_complete(run_client(address, loop, timeout=timeout))
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("BLE", description="Example Bluetooth LE interaction client")
    parser.add_argument(
        "-t", "--timeout", action="store", type=int, help="Connection timeout", required=False, default=10)
    args = parser.parse_args()

    try:
        main(timeout=args.timeout)
    except KeyboardInterrupt:
        print("LATER!")
    except BleakError as e:
        print(f"BleakError: {e}")
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-except
        print(f"Unhandled exception: {e}")
        traceback.print_exc()
        sys.exit(1)

    print("Done!")
    sys.exit(0)
