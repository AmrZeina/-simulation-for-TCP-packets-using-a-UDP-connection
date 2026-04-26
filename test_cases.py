import time
from threading import Thread
from reliable_udp import ReliableUDP
from server import http_server
from client import http_client

def test_handshake():
    print("\nTest 1: handshake")

    def server():
        s = ReliableUDP("127.0.0.1", 8080, is_server=True)
        s.accept()
        print("Server: Handshake OK")
        s.close()

    def client():
        time.sleep(1)
        c = ReliableUDP("127.0.0.1", 8080)
        c.connect()
        print("Client: Handshake OK")
        c.close()

    server_thread = Thread(target=server)
    client_thread = Thread(target=client)
    server_thread.start()
    client_thread.start()
    server_thread.join(timeout=5)
    client_thread.join(timeout=5)
    time.sleep(2)  # Allow socket to release



def test_retransmission():
    print("\nTest 2: retransmission")

    def server():
        s = ReliableUDP("127.0.0.1", 8081, is_server=True)
        s.accept()
        msg, _ = s.receive()
        print("Server received:", msg)
        s.close()

    def client():
        time.sleep(1)
        c = ReliableUDP("127.0.0.1", 8081)
        c.connect()
        c.send("Test Message with Loss")
        time.sleep(1)
        c.close()

    server_thread = Thread(target=server)
    client_thread = Thread(target=client)
    server_thread.start()
    client_thread.start()
    server_thread.join(timeout=10)
    client_thread.join(timeout=10)
    time.sleep(2)



def test_duplicate():
    print("\nTest 3: duplicate handling")

    def server():
        s = ReliableUDP("127.0.0.1", 8082, is_server=True)
        s.accept()
        msg, _ = s.receive()
        print("Server received first:", msg)
        msg2, _ = s.receive()
        print("Server received second:", msg2)
        s.close()

    def client():
        time.sleep(1)
        c = ReliableUDP("127.0.0.1", 8082)
        c.connect()
        c.send("Duplicate Test")
        time.sleep(0.5)
        c.send_seq = 0  # Force duplicate
        c.send("Duplicate Test")
        time.sleep(1)
        c.close()

    server_thread = Thread(target=server)
    client_thread = Thread(target=client)
    server_thread.start()
    client_thread.start()
    server_thread.join(timeout=10)
    client_thread.join(timeout=10)
    time.sleep(2)


if __name__ == "__main__":
    test_handshake()
    test_retransmission()
    test_duplicate()

    print("All tests completed!")