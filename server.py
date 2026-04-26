from reliable_udp import ReliableUDP

def parse_http_request(request):
    lines = request.split("\r\n")

    method, path, version = lines[0].split()

    headers = {}
    i = 1
    while lines[i] != "":
        key, value = lines[i].split(": ", 1)
        headers[key] = value
        i += 1

    body = "\r\n".join(lines[i+1:])
    return method, path, headers, body


def http_server():
    server = ReliableUDP("127.0.0.1", 8080, is_server=True)
    server.accept()

    while True:
        data, addr = server.receive()
        print("\nHTTP Request:\n", data)

        if data is None:
            server.close()
            return
    
        method, path, headers, body = parse_http_request(data)

        if method == "GET":
            if path == "/":
                response_body = "Home Page"
            elif path == "/hello":
                response_body = "Hello, World! from server."
            elif path == "/file":
                try:
                    with open("test.txt", "r") as f:
                        response_body = f.read()
                except:
                    response = "HTTP/1.0 404 NOT FOUND\r\n\r\n"
                    server.send(response)
                    server.close()
                    return
            else:
                response = "HTTP/1.0 404 NOT FOUND\r\n\r\n"
                server.send(response)
                server.close()
                return
                

        elif method == "POST":
            length = int(headers.get("Content-Length", 0))
            print("POST body:", body[:length])
            response_body = "POST received"

        else:
            response = "HTTP/1.0 404 NOT FOUND\r\n\r\n"
            server.send(response)
            server.close()
            return

        response = (
            "HTTP/1.0 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(response_body)}\r\n"
            "\r\n"
            + response_body
        )

        server.send(response)


if __name__ == "__main__":
    http_server()