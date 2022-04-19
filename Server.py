from socket import *
from Record import Record

# Zachary Pownell
# 18 April, 2022
# UDPServer source code file. Used to send OFFER, ACKNOWLEDGE, DECLINE, and LIST messages to UDPClients. Will listen for
# DISCOVER, REQUEST, RELEASE, RENEW, and LIST messages from clients. Stores a list of available IP addresses for clients
# and keeps a record of every client that has sent a message.


print("[SERVER] Starting server...")
SERVER_PORT = 18000
SERVER_SOCKET = socket(AF_INET, SOCK_DGRAM)
SERVER_SOCKET.bind(('', SERVER_PORT))

LEASE_TIME = 60  # Lease time, in seconds.
records = []  # List to store records of clients that have communicated with server.
available_ip_addresses = ["192.168.45.15", "192.168.45.14", "192.168.45.13", "192.168.45.12", "192.168.45.11",
                          "192.168.45.10", "192.168.45.9", "192.168.45.8", "192.168.45.7", "192.168.45.6",
                          "192.168.45.5", "192.168.45.4", "192.168.45.3", "192.168.45.2", "192.168.45.1"]

print(f"[SERVER] IP Addresses available for use:\n{available_ip_addresses}")
print('[SERVER] The server is ready to receive...\n')


# ------------

def print_records_and_ips():
    print("------------------------------------------------------------------------------------")
    print(f"AVAILABLE IP ADDRESSES:\n{available_ip_addresses}\nRECORDS:")
    for record in records:
        print(f"Mac Address: {record.mac_address} -- {record.ip_address} -- " f"{record.timestamp} -- "
              f"{record.acknowledged}")
    print("------------------------------------------------------------------------------------\n\n")


# -------------------------------- SERVER: SEND MESSAGE FUNCTIONS --------------------------------


def send_offer_message(mac_address, ip_address, timestamp):
    offer_message = f"1,{mac_address},{ip_address},{timestamp}"
    print(f"[SERVER] Sent OFFER message to client {mac_address} :\n{offer_message}")
    print_records_and_ips()
    SERVER_SOCKET.sendto(offer_message.encode(), client_address)


def send_acknowledge_message(mac_address, ip_address, timestamp):
    acknowledge_message = f"3,{mac_address},{ip_address},{timestamp}"
    print(f"[SERVER] Sent ACKNOWLEDGE message to client {mac_address} :\n{acknowledge_message}")
    print_records_and_ips()
    SERVER_SOCKET.sendto(acknowledge_message.encode(), client_address)


def send_decline_message(mac_address, message):
    decline_message = f"7,{mac_address},{message}"
    print(f"[SERVER] Sent DECLINE message to client {mac_address} :\n{decline_message}")
    print_records_and_ips()
    SERVER_SOCKET.sendto(decline_message.encode(), client_address)


def send_list_message(message):
    list_message = f"6,{message}"
    print(f"[SERVER] Sent LIST message to admin client\n{list_message}")
    print_records_and_ips()
    SERVER_SOCKET.sendto(list_message.encode(), client_address)


# -------------------------------- SERVER: RECEIVED MESSAGE FUNCTIONS --------------------------------


def received_discover_message(mac_address):
    print(f"[SERVER] Received DISCOVER message from client {mac_address}")
    print(f"[SERVER] IP addresses are available:\n{available_ip_addresses}")
    print(f"[SERVER] Searching records for {mac_address}...")

    for record in records:

        if record.mac_address == mac_address:  # A record has been found

            print("[SERVER] Record has been found. Checking timestamp...")

            if record.timestamp > 0:

                print("[SERVER] Timestamp is still active, sending acknowledge message")
                send_acknowledge_message(mac_address, record.ip_address, record.timestamp)
                return

            else:  # The timestamp has expired.

                print("[SERVER] Timestamp has expired. Checking if previous IP address still available...")

                if record.ip_address in available_ip_addresses:
                    print(f"[SERVER] IP address {record.ip_address} is currently available, sending offer message...")
                    send_offer_message(mac_address, record.ip_address, record.timestamp)
                    return

                if len(available_ip_addresses) > 0:
                    send_offer_message(mac_address, available_ip_addresses[-1], record.timestamp)
                    return

                send_decline_message(mac_address, "No available IP addresses in server.")
                return

    print("[SERVER] Could not find record of client. Verifying if available IP address exists...")

    if len(available_ip_addresses) == 0:
        print("No available IP addresses for client, sending decline message...")
        send_decline_message(mac_address, "No available IP addresses for client")
        return

    print("[SERVER] Available IP address exists. Adding client to records and sending offer message...")
    new_record = Record(mac_address, available_ip_addresses[-1], 60, False)
    records.append(new_record)
    send_offer_message(mac_address, available_ip_addresses[-1], 0)


def received_request_message(mac_address, ip_address):
    print(f"[SERVER] Received REQUEST message from client {mac_address}")
    print("[SERVER] Verifying records of client...")

    for record in records:

        if record.mac_address == mac_address:

            print(f"[SERVER] Found client in records. Checking if IP address {ip_address} is still available...")

            if ip_address in available_ip_addresses:

                print(f"[SERVER] IP address {ip_address} is still available for client. Assigning...")
                available_ip_addresses.remove(ip_address)
                record.set_ip_address(ip_address)
                if record.timestamp == 0:
                    send_decline_message(mac_address, "Timestamp for this record is 0.")
                    return
                record.set_acknowledged(True)
                record.set_timestamp(LEASE_TIME)
                print(f"[SERVER] IP address {ip_address} successfully assigned to client")
                print(f"[SERVER] New available IP addresses:\n{available_ip_addresses}")
                print(f"[SERVER] Sending acknowledge message to client {mac_address}...")
                send_acknowledge_message(mac_address, ip_address, record.timestamp)
                return

    if len(available_ip_addresses) == 0:
        print(f"[SERVER] Offered IP {ip_address} no longer available for client. Sending decline message...")
        send_decline_message(mac_address, "No available IP addresses")
        return

    print(f"[SERVER] MAC address not found in records. Sending decline message...")
    send_decline_message(mac_address, "Could not find client in records.")


def received_release_message(mac_address):
    print(f"[SERVER] Received RELEASE message from client {mac_address}")
    print(f"[SERVER] Checking records for client...")

    for record in records:

        if record.mac_address == mac_address:

            print(f"[SERVER] Found record of client.")

            if record.ip_address not in available_ip_addresses:
                print("[SERVER] Making IP address available.")
                available_ip_addresses.append(record.ip_address)

            record.set_timestamp(0)
            record.set_acknowledged(False)
            break

    print(f"[SERVER] Client {mac_address} successfully released.")
    print_records_and_ips()


def received_renew_message(mac_address):
    print(f"[SERVER] Received RENEW message from client {mac_address}")
    print("[SERVER] Searching records for client...")
    for record in records:

        if record.mac_address == mac_address:

            print("[SERVER] Found records of client. Checking if client is acknowledged...")
            if record.acknowledged:
                print("[SERVER] Client already acknowledged. Sending acknowledge message...")
                send_acknowledge_message(mac_address, record.ip_address, record.timestamp)
                return

            print("[SERVER] Client not acknowledged. Making acknowledged checking if previous IP still available...")
            record.set_timestamp(LEASE_TIME)
            record.set_acknowledged(True)

            if record.ip_address in available_ip_addresses:

                print("[SERVER] Previously used IP address is still available. Sending acknowledge message...")
                available_ip_addresses.remove(record.ip_address)
                print(f"[SERVER] New available IP addresses:\n{available_ip_addresses}")
                print(f"[SERVER] Sending acknowledge message to client...")
                send_acknowledge_message(mac_address, record.ip_address, record.timestamp)
                return

            else:

                print("[SERVER] Previously used IP address is not available. Checking for available IP address...")

                if len(available_ip_addresses) == 0:
                    print("[SERVER] No available IP addresses for client. Sending decline message...")
                    send_decline_message(mac_address, "No available IP addresses.")
                    return

                print("[SERVER] IP address available for client. Sending offer message...")
                send_offer_message(mac_address, available_ip_addresses[-1], record.timestamp)
                return

    print("[SERVER] Could not find a record of client. Sending decline message...")
    send_decline_message(mac_address, "No such client in records exists.")


def received_list_message():
    list_message = ""

    if records:
        for record in records:
            list_message += f"Mac Address: {record.mac_address} -- {record.ip_address} -- " \
                            f"{record.timestamp} -- {record.acknowledged}\n"
        send_list_message(list_message)
        return
    send_list_message("Records are empty.")


# -------------------------------- SERVER: LISTENER --------------------------------


while 1:

    received_message, client_address = SERVER_SOCKET.recvfrom(2048)
    received_message = received_message.decode()
    split_received_message = received_message.split(',')
    message_type = split_received_message[0]
    received_mac_address = split_received_message[1]

    print(f"[SERVER] Receiving type '{message_type}' message from client. Decoding...")

    # DISCOVER
    if message_type == '0':
        received_discover_message(received_mac_address)

    # REQUEST
    if message_type == '2':
        received_request_message(received_mac_address, split_received_message[2])

    # RELEASE
    if message_type == '4':
        received_release_message(received_mac_address)

    # RENEW
    if message_type == '5':
        received_renew_message(received_mac_address)

    # LIST
    if message_type == '6':
        received_list_message()
