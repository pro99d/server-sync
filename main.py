import socket
import json

class Server:
    def __init__(self, port: int, type: str= "tcp"):
        self.port = port
        self.type = type
        self.hostname = "0.0.0.0"
        if type == "tcp":
            self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.listen(5)
        elif type == "udp":
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            raise ValueError(f"unsupported type {type}")

        self.socket.bind((self.hostname, self.port))
        self.data = {}
    def get_data(self, conn):
        if self.type == "tcp":
            length_bytes = conn.recv(4)
            length = int.from_bytes(length_bytes, byteorder='big')
            data_bytes = conn.recv(length)
            return json.loads(data_bytes.decode('utf-8'))
        elif self.type == "udp":
            data, addr = conn.recvfrom(1024)
            return json.loads(data.decode('utf-8'))

    def send_data(self, data, conn, addr=None):
        data = json.dumps(data).encode('utf-8')
        if self.type == "tcp":
            length = len(data)
            conn.sendall(length.to_bytes(4, byteorder='big') + data)
        elif self.type == "udp":
            if addr:
                conn.sendto(data, addr)


    def update_data(self, data):
        self.data.update(data)

    def listen(self):
        if self.type == "tcp":
            conn, addr = self.socket.accept()
            print(f"tcp by {addr}")
            try:
                data = self.get_data(conn)
                request_type = data['type']
                if request_type == "update":
                    self.update_data(data["data"])
                    print(self.data)
                elif request_type == "get":
                    self.send_data(self.data, conn)
                elif request_type == "clear":
                    self.data.clear()
            finally:
                conn.close()
        elif self.type == "udp":
            data, addr = self.socket.recvfrom(1024)
            data = json.loads(data.decode('utf-8'))
            request_type = data['type']
            if request_type == "update":
                self.update_data(data["data"])
            elif request_type == "get":
                self.send_data(self.data, self.socket, addr)
            elif request_type == "clear":
                self.data.clear()

class Client:
    def __init__(self, host: str, port: int, type: str = "tcp"):
        self.host = host
        self.port = port
        self.type = type

    def _create_socket(self):
        if self.type == "tcp":
            return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif self.type == "udp":
            return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            raise ValueError(f"unsupported type {type}")

    def _send_request(self, request):
        sock = self._create_socket()
        try:
            if self.type == "tcp":
                sock.connect((self.host, self.port))
            request_data = json.dumps(request).encode('utf-8')
            if self.type == "tcp":
                length = len(request_data)
                sock.sendall(length.to_bytes(4, byteorder='big') + request_data)
            elif self.type == "udp":
                sock.sendto(request_data, (self.host, self.port))
            return sock
        except Exception:
            sock.close()
            raise

    def _receive_response(self, sock):
        try:
            if self.type == "tcp":
                length_bytes = sock.recv(4)
                length = int.from_bytes(length_bytes, byteorder='big')
                response_bytes = sock.recv(length)
                return json.loads(response_bytes.decode('utf-8'))
            elif self.type == "udp":
                response_bytes, addr = sock.recvfrom(1024)
                return json.loads(response_bytes.decode('utf-8'))
        finally:
            sock.close()

    def update(self, data):
        request = {
            "type": "update",
            "data": data
        }
        sock = self._send_request(request)
        # For update, we don't need to receive a response, just close the socket
        sock.close()

    def get(self):
        request = {
            "type": "get",
            "data": None
        }
        sock = self._send_request(request)
        return self._receive_response(sock)

    def clear(self):
        request = {
            "type": "clear",
            "data": None
        }
        sock = self._send_request(request)
        # For clear, we don't need to receive a response, just close the socket
        sock.close()


def main():
    print("Hello from server-sync!")


if __name__ == "__main__":
    main()
