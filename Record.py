
# Zachary Pownell
# 18 April, 2022
# Record class source code file. Record objects contain a MAC address, IP address, timestamp, and an acknowledged flag.
# Store these objects in the UDPServer records list for easy management of record keeping. Contains modifiers for
# timestamp, IP address, and acknowledged flag.


class Record:

    def __init__(self, mac_address, ip_address, timestamp, acknowledged):
        self.mac_address = mac_address
        self.ip_address = ip_address
        self.timestamp = timestamp
        self.acknowledged = acknowledged

    def set_timestamp(self, new_timestamp):
        self.timestamp = new_timestamp

    def set_ip_address(self, new_ip_address):
        self.ip_address = new_ip_address

    def set_acknowledged(self, new_acknowledged):
        self.acknowledged = new_acknowledged
