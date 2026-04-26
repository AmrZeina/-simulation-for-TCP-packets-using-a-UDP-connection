import socket
from reliable_udp import ReliableUDP

TCP_IP = "127.0.0.1"
TCP_PORT = 8000 
UDP_IP = "127.0.0.1"
UDP_PORT = 8080 

def start_proxy():
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind((TCP_IP, TCP_PORT))
    tcp_sock.listen(5)

    print(f"Proxy listening on http://{TCP_IP}:{TCP_PORT}")

    while True:
        conn, addr = tcp_sock.accept()
        print("Browser connected:", addr)

        request = conn.recv(4096).decode()
        print("\nBrowser Request:\n", request)

        client = ReliableUDP(UDP_IP, UDP_PORT)
        client.connect()

        client.send(request)
        response, _ = client.receive()

        conn.sendall(response.encode())
        conn.close()

        client.close()

if __name__ == "__main__":
    start_proxy()