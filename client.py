from main import Client

def main():
    client = Client("localhost", 9000, "udp")
    data = {"test_data1":3}
    client.update(data)
    nd = client.get()
    print(nd)

if __name__ == "__main__":
    main()
