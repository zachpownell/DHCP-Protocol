import re
import string
import uuid
from socket import *
import random


# Zachary Pownell
# 18 April, 2022
# UDPClient source code file. Used to send DISCOVER, REQUEST, RELEASE, and RENEW messages to UDPServer. Will listen for
# OFFER, ACKNOWLEDGE, and DECLINE messages from the server.


SERVER_NAME = 'localhost'
SERVER_PORT = 18000
CLIENT_SOCKET = socket(AF_INET, SOCK_DGRAM)
client_ip_address = ""

# Use this if we want to use the client's actual MAC address.
CLIENT_MAC_ADDRESS = (':'.join(re.findall('..', '%012x' % uuid.getnode())))
# Use the generate_mac_address function to generate arbitrary random MAC addresses for testing.

print(f"[CLIENT] Starting client with MAC ID {CLIENT_MAC_ADDRESS}...")


# -------------------------------- CLIENT: MAC ID GENERATOR (for testing) --------------------------------


def generate_mac_address():

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


# CLIENT_MAC_ADDRESS = generate_mac_address()
print(f"[CLIENT] MAC Address: {CLIENT_MAC_ADDRESS}\n")


# -------------------------------- CLIENT: SEND MESSAGE FUNCTIONS --------------------------------


def send_discover_message():
    discover_message = f"0,{str(CLIENT_MAC_ADDRESS)}"
    CLIENT_SOCKET.sendto(discover_message.encode(), (SERVER_NAME, SERVER_PORT))
    print(f"[CLIENT] Sent DISCOVER message to server:\n{discover_message}\n")


def send_request_message(mac_address, ip_address, timestamp):
    request_message = f"2,{str(mac_address)},{str(ip_address)},{str(timestamp)}"
    CLIENT_SOCKET.sendto(request_message.encode(), (SERVER_NAME, SERVER_PORT))
    print(f"[CLIENT] Sent REQUEST message to server:\n{request_message}\n")


def send_release_message():
    release_message = f"4,{str(CLIENT_MAC_ADDRESS)}"
    CLIENT_SOCKET.sendto(release_message.encode(), (SERVER_NAME, SERVER_PORT))
    print(f"[CLIENT] Sent RELEASE message to server:\n{release_message}\n")


def send_renew_message():
    renew_message = f"5,{str(CLIENT_MAC_ADDRESS)}"
    CLIENT_SOCKET.sendto(renew_message.encode(), (SERVER_NAME, SERVER_PORT))
    print(f"[CLIENT] Sent RENEW message to server:\n{renew_message}\n")


# -------------------------------- CLIENT: RECEIVED MESSAGE FUNCTIONS --------------------------------


def received_offer_message(offered_mac_address, offered_ip_address, offered_timestamp):
    print(f"[CLIENT] Received OFFER message from server")
    if offered_mac_address != CLIENT_MAC_ADDRESS:
        print(f"[CLIENT] Could not verify MAC address {offered_mac_address} to {CLIENT_MAC_ADDRESS}. Terminating...")
        exit(1)
    if offered_timestamp == 0:
        print(f"[CLIENT] Timestamp expired for {offered_mac_address}. Terminating...")
        exit(1)
    print("[CLIENT] MAC Address verified. Sending request message...")
    send_request_message(offered_mac_address, offered_ip_address, offered_timestamp)


def received_acknowledge_message(acknowledged_mac_address, acknowledged_ip_address, acknowledged_timestamp):
    print(f"[CLIENT] Received ACKNOWLEDGE message from server {server_address}")
    if acknowledged_mac_address != CLIENT_MAC_ADDRESS:
        print(f"[CLIENT] Acknowledged IP address and client IP address do not match. Terminating...")
        exit(1)
    print(f"\n[CLIENT] IP ADDRESS {acknowledged_ip_address} ASSIGNED TO THIS CLIENT. WILL EXPIRE IN {acknowledged_timestamp} SECONDS.\n")
    global client_ip_address
    client_ip_address = acknowledged_ip_address


def received_decline_message(message):

    print(f"[CLIENT] Received DECLINED message from server {server_address}:\n{message}\n")
    exit(1)


# -------------------------------- CLIENT: RUNNER --------------------------------


print("[CLIENT] Sending discover message...\n")
send_discover_message()

while client_ip_address == "":

    received_message, server_address = CLIENT_SOCKET.recvfrom(2048)
    received_message = received_message.decode()
    split_received_message = received_message.split(',')
    message_type = split_received_message[0]
    received_mac_address = split_received_message[1]
    print(f"[CLIENT] Receiving type '{message_type}' message from server. Decoding...")

    if message_type == '1':
        received_offer_message(received_mac_address, split_received_message[2], split_received_message[3])
    if message_type == '3':
        received_acknowledge_message(received_mac_address, split_received_message[2], split_received_message[3])
        break
    if message_type == '7':
        received_decline_message(split_received_message[2])

while 1:
    user_input = input("Enter 'r' for release, 'n' for renew, 'q' for quit: ")

    if user_input == 'r':
        send_release_message()

    if user_input == 'n':
        send_renew_message()

        received_message, server_address = CLIENT_SOCKET.recvfrom(2048)
        received_message = received_message.decode()
        split_received_message = received_message.split(',')
        message_type = split_received_message[0]
        received_mac_address = split_received_message[1]
        print(f"[CLIENT] Receiving type '{message_type}' message from server. Decoding...")

        if message_type == '1':
            received_offer_message(received_mac_address, split_received_message[2], split_received_message[3])
        if message_type == '3':
            received_acknowledge_message(received_mac_address, split_received_message[2], split_received_message[3])
        if message_type == '7':
            received_decline_message(split_received_message[2])

    if user_input == 'q':
        exit(0)
