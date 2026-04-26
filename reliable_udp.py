import socket
import time
import random
import json

# Constants
TIMEOUT = 2
LOSS_PROB = 0.2
CORRUPT_PROB = 0.1

class ReliableUDP:
    def __init__(self, ip, port, is_server=False):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT)
        self.addr = (ip, port)
        self.seq = 0
        self.expected_seq = 0
        self.is_server = is_server
        self.connected_addr = None

        if is_server:
            self.sock.bind(self.addr)

    # -----------------------
    # CHECKSUM
    # -----------------------
    def checksum(self, data):
        return sum(bytearray(data.encode())) % 256

    # -----------------------
    # CREATE PACKET
    # -----------------------
    def make_packet(self, data, flags=""):
        packet = {
            "seq": self.seq,
            "ack": 0,
            "flags": flags,
            "data": data
        }
        packet["checksum"] = self.checksum(data)
        return json.dumps(packet)

    # -----------------------
    # SIMULATE LOSS
    # -----------------------
    def simulate_loss(self):
        return random.random() < LOSS_PROB

    # -----------------------
    # SIMULATE CORRUPTION
    # -----------------------
    def simulate_corruption(self, packet):
        if random.random() < CORRUPT_PROB:
            return packet[:-1] + "X"
        return packet

    # -----------------------
    # SEND WITH RETRANSMISSION
    # -----------------------
    def send(self, data):
        packet = self.make_packet(data)

        while True:
            if not self.simulate_loss():
                corrupted = self.simulate_corruption(packet)
                self.sock.sendto(corrupted.encode(), self.addr)
                print(f"Sent: {packet}")

            try:
                ack_data, _ = self.sock.recvfrom(2048)
                ack = json.loads(ack_data.decode())

                if ack["flags"] == "ACK" and ack["ack"] == self.seq:
                    print("ACK received")
                    self.seq += 1
                    break

            except socket.timeout:
                print("Timeout → Resending...")

    # -----------------------
    # RECEIVE
    # -----------------------
    def receive(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(2048)

                if self.simulate_loss():
                    print("Packet lost")
                    continue

                packet = json.loads(data.decode())

                # Check checksum
                if packet["checksum"] != self.checksum(packet["data"]):
                    print("Corrupted packet → dropped")
                    continue

                # Check sequence
                if packet["seq"] != self.expected_seq:
                    print("Duplicate or out-of-order → ignored")
                    continue

                if packet["flags"] == "FIN":
                    print("FIN received → closing connection")
                    self.sock.close()
                    exit()

                print(f"Received: {packet}")

                # Send ACK
                ack_packet = {
                    "seq": 0,
                    "ack": packet["seq"],
                    "flags": "ACK",
                    "data": ""
                }
                    
                self.sock.sendto(json.dumps(ack_packet).encode(), addr)
                self.expected_seq += 1

                return packet["data"], addr

            except:
                continue

    # -----------------------
    # HANDSHAKE (CLIENT)
    # -----------------------
    def connect(self):
        syn_packet = {
            "seq": self.seq,
            "ack": 0,
            "flags": "SYN",
            "data": ""
        }
        self.sock.sendto(json.dumps(syn_packet).encode(), self.addr)

        while True:
            try:
                data, _ = self.sock.recvfrom(2048)
                packet = json.loads(data.decode())

                if packet["flags"] == "SYN-ACK":
                    ack_packet = {
                        "seq": self.seq,
                        "ack": packet["seq"],
                        "flags": "ACK",
                        "data": ""
                    }
                    self.sock.sendto(json.dumps(ack_packet).encode(), self.addr)
                    print("Connected!")
                    break
            except:
                continue

    # -----------------------
    # HANDSHAKE (SERVER)
    # -----------------------
    def accept(self):
        self.sock.settimeout(None)

        while True:
            try:
                data, addr = self.sock.recvfrom(2048)
                packet = json.loads(data.decode())

                if packet["flags"] == "SYN":
                    syn_ack = {
                        "seq": 0,
                        "ack": packet["seq"],
                        "flags": "SYN-ACK",
                        "data": ""
                    }
                    self.sock.sendto(json.dumps(syn_ack).encode(), addr)

                    data, _ = self.sock.recvfrom(2048)
                    final = json.loads(data.decode())

                    if final["flags"] == "ACK":
                        print("Client connected")
                        self.addr = addr
                        break

            except:
                continue
    # -----------------------
    # CLOSE CONNECTION
    # -----------------------
    def close(self):
        fin = {"seq": self.seq, "ack": 0, "flags": "FIN", "data": ""}
        self.sock.sendto(json.dumps(fin).encode(), self.addr)
        print("Connection closed")