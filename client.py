from reliable_udp import ReliableUDP

def http_client():
    client = ReliableUDP("127.0.0.1", 8080)
    client.connect()

    # Get Request
    request = (
        "GET /hello HTTP/1.0\r\n"
        "Host: localhost\r\n"
        "\r\n"
    )

    client.send(request)
    response, _ = client.receive()
    print("\nResponse:\n", response)

    # Post Request
    body = "Hello World"
    request = (
        "POST / HTTP/1.0\r\n"
        "Host: localhost\r\n"
        f"Content-Length: {len(body)}\r\n"
        "\r\n"
        + body
    )

    client.send(request)
    response, _ = client.receive()
    print("\nResponse:\n", response)
    client.close()


if __name__ == "__main__":
    http_client()