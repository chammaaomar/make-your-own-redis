import socket
import asyncio
import threading
import re
import time

ARRAY = ord("*")
INT = ord(":")
ECHO = b"ECHO"
SET = b"SET"
GET = b"GET"
PING = b"PING"
PX = b"PX"
BSTRING = ord("$")
CMDS = [
    "ECHO",
    "PING",
    "SET",
    "GET",
]

REDIS_DB = {}


def main():
    print("Implement your Redis server here!")

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
                target=handle_ping, args=(conn, addr)))
            threads[-1].start()


def handle_ping(conn, addr):
    data = b""
    with conn:
        while data != b"quit\r\n":
            data = conn.recv(1024)
            # special form of PING command
            if data == "+PING\r\n":
                conn.sendall("$4\r\nPONG\r\n")
            data_tokens = data.rstrip(b"\r\n").split(b"\r\n")
            if len(data_tokens) < 3:
                error(conn, "Too few arguments passed. Please check.")
                continue
            array_spec, *array = data_tokens
            if bad_array_format(array_spec, array):
                error(conn, "Array formatting is not RESP-compliant. Please check.")
                continue
            cmd_spec, cmd, *args = array
            if bad_string_format(cmd_spec, cmd):
                error(conn, "Command formatting is not RESP-compliant. Please check.")
                continue
            try:
                res = handle_request(cmd, args)
                conn.sendall(res)
            except (ValueError, NotImplementedError) as e:
                error(conn, str(e))
                continue


def bad_array_format(array_spec, array):
    """
    Checks if request is RESP-compliant. Should be an array of bulk strings
    """
    if array_spec[0] != ARRAY:
        return True
    arr_len = int(array_spec[1:], base=10)
    if 2 * arr_len != len(array):
        return True
    return False


def error(conn, msg):
    res = bytes(f"-Error: {msg}\r\n", "utf-8")
    conn.sendall(res)
    return


def bad_string_format(string_spec, string):
    if string_spec[0] != BSTRING:
        return True
    str_len = int(string_spec[1:], base=10)
    if str_len != len(string):
        return True
    return False


def safe_index(array, item):
    try:
        return array.index(item)
    except ValueError:
        return -1


def expire_key(key, ttl):
    time.sleep(ttl / 1000.0)
    del REDIS_DB[key]


def handle_request(cmd, args):
    if cmd.upper() == ECHO:
        if len(args) > 2:
            raise ValueError("ECHO expects a single bulk string.")
        if bad_string_format(args[0], args[1]):
            raise ValueError(
                "Arg formatting is not RESP-compliant. Please check.")

        # e.g. $2\r\nOK\r\n
        return b"\r\n".join([*args, b""])
    elif cmd.upper() == PING:
        if len(args) > 2:
            raise ValueError(
                "PING expects a single bulk string as message or no message.")
        if len(args) == 2 and bad_string_format(args[0], args[1]):
            raise ValueError(
                "Arg formatting is not RESP-compliant. Please check.")
        return b"$4\r\nPONG\r\n"
    elif cmd.upper() == SET:
        if len(args) < 3:
            raise ValueError("SET expects a KEY and a VALUE")
        if bad_string_format(args[0], args[1]):
            raise ValueError(
                "Arg formatting is not RESP-compliant. Please check.")
        key = args[1]
        data_type = args[2][0]
        if data_type == INT:
            value = args[2][1:]
            REDIS_DB[key] = int(value, base=10)
            opt_indx = 3
        elif data_type == BSTRING:
            if bad_string_format(args[2], args[3]):
                raise ValueError(
                    "Arg formatting is not RESP-compliant. Please check.")
            REDIS_DB[key] = str(args[3], encoding="utf-8")
            opt_indx = 4
        opts = args[opt_indx:]
        exp_indx = safe_index(opts, PX)
        if exp_indx > -1:
            if (bad_string_format(opts[exp_indx - 1], opts[exp_indx])
                    or bad_string_format(opts[exp_indx + 1], opts[exp_indx + 2])):
                raise ValueError(
                    "Options formatting is not RESP-compliant. Please check.")
            ttl = int(opts[exp_indx + 2], base=10)
            print(ttl)
            expiry_thread = threading.Thread(
                target=expire_key, args=(key, ttl))
            expiry_thread.start()
        return b"$2\r\nOK\r\n"
    elif cmd.upper() == GET:
        if len(args) != 2:
            raise ValueError("GET expects a single key")
        if bad_string_format(args[0], args[1]):
            raise ValueError(
                "Arg formatting is not RESP-compliant. Please check.")
        value = REDIS_DB.get(args[1], None)
        if value is None:
            return b"$-1\r\n"
        if type(value) is int:
            return b":" + bytes(str(value), encoding="utf-8") + b"\r\n"
        if type(value) is str:
            length_bytes = bytes(str(len(value)), encoding="utf-8")
            return b"$" + length_bytes + b"\r\n" + bytes(value, encoding="utf-8") + b"\r\n"
    else:
        raise NotImplementedError(
            f"Only {','.join(CMDS)} have been implemented.")


if __name__ == "__main__":
    main()
