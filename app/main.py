def main():
    print("Implement your Redis server here!")

    # Uncomment this to pass the first stage
    #
    import socket
    # localhost (loopback interface; processes on host talk only)
    HOST = "127.0.0.1"
    PORT = 6379  # default redis port; unprivileged > 1023
    # AF === address family; chose IPv4. SOCKET_STREAM speicifies TCP
    # reliable (detect and resend lost packets); data arrives in-order of send
    # there is UDP: socket.SOCK_DGRAM
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as sock:
        # option name: reuse_addr, value = 1
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen()  # takes backlog (queue) int parameter for pending connections
        # accept is blocking; returns a new socket object; use this to talk to client
        # IPv4 address is (client-host, client-port)
        connection, address = sock.accept()
        with connection:
            print('Welcome to Redis server!', address)
            while True:
                # blocking
                data = connection.recv(1024)
                connection.send(b"+PONG\r\n")
                break


if __name__ == "__main__":
    main()
