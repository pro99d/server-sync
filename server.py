from main import Server

def main():
    server = Server(9000, "udp")
    while True:
        server.listen()
if __name__ == "__main__":
    main()
