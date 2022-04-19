import re
import uuid
from socket import *


# Zachary Pownell
# 18 April, 2022
# UDPAdminClient source code file. Used to send a LIST message to the server and will return a list of all records of
# MAC addresses that have connected to the server, along with their associated IP address, timestamp, and acknowledged
# flag.


SERVER_NAME = 'localhost'
SERVER_PORT = 18000
CLIENT_SOCKET = socket(AF_INET, SOCK_DGRAM)

print("[ADMIN CLIENT] Starting admin client...")
CLIENT_MAC_ADDRESS = (':'.join(re.findall('..', '%012x' % uuid.getnode())))


# -------------------------------- ADMIN CLIENT: SEND MESSAGE FUNCTIONS --------------------------------


def send_list_message():
    list_message = f"6,{str(CLIENT_MAC_ADDRESS)}"
    CLIENT_SOCKET.sendto(list_message.encode(), (SERVER_NAME, SERVER_PORT))
    print(f"[ADMIN CLIENT] Sent LIST message to server:\n{list_message}\n")
    pass


# -------------------------------- ADMIN CLIENT: RECEIVED MESSAGE FUNCTIONS --------------------------------


def received_list_message(message):
    print(f"[ADMIN CLIENT] Received LIST message from server {server_address}:\n{message}\n")


# -------------------------------- ADMIN CLIENT: RUNNER --------------------------------


print("[ADMIN CLIENT] Sending list message...\n")
send_list_message()

received_message, server_address = CLIENT_SOCKET.recvfrom(2048)
received_message = received_message.decode()
split_received_message = received_message.split(',')
message_type = received_message[0]
print(f"[ADMIN CLIENT] Receiving type '{message_type}' message from server. Decoding...")

if message_type == '6':
    received_list_message(split_received_message[1])
    exit(0)

exit(1)
