import socket
import threading

import app.handlers as handlers
import app.resp as RESP
import app.utils as utils


def main():
    print("Welcome to O-Redis!")

    # Uncomment this to pass the first stage
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
        threads = []
        while True:
            conn, addr = sock.accept()
            threads.append(threading.Thread(
                target=handle_connection, args=(conn, addr)))
            threads[-1].start()


def handle_connection(conn, addr):
    data = b""
    with conn:
        while data != RESP.sstring("quit") or data != RESP.bstring("quit"):
            data = conn.recv(1024)
            # special form of PING command
            if data.upper() == RESP.sstring("PING"):
                conn.sendall(RESP.bstring("PONG"))
            data_tokens = data.rstrip(b"\r\n").split(b"\r\n")
            if len(data_tokens) < 3:
                utils.error(conn, "Too few arguments passed. Please check.")
                continue
            if utils.bad_cmd_format(data_tokens):
                utils.error(
                    conn, "Array formatting is not RESP-compliant. Please check.")
                continue
            cmd, *args = data_tokens[2:]
            try:
                res = handle_request(cmd, args)
                conn.sendall(res)
            except (ValueError, NotImplementedError) as e:
                utils.error(conn, str(e))
                continue


def handle_request(cmd, args):
    if cmd.upper() == RESP.ECHO:
        if len(args) != 2:
            raise ValueError("ECHO expects a single bulk string.")
        return handlers.handle_echo(args)
    elif cmd.upper() == RESP.PING:
        if len(args) > 2:
            raise ValueError(
                "PING expects a single bulk string as message or no message.")
        return handlers.handle_ping(args)
    elif cmd.upper() == RESP.SET:
        if len(args) < 3:
            raise ValueError("SET expects a KEY and a VALUE")
        return handlers.handle_set(args)
    elif cmd.upper() == RESP.GET:
        if len(args) != 2:
            raise ValueError("GET expects a single key")
        return handlers.handle_get(args)
    else:
        raise NotImplementedError(
            f"Only {','.join(RESP.CMDS)} have been implemented.")


if __name__ == "__main__":
    main()
