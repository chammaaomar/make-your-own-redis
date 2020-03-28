ARRAY = ord("*")
INT = ord(":")
SSTRING = ord("+")
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
NIL = b"$-1\r\n"


def sstring(string):
    bytes_str = bytes(string, encoding="utf-8")
    return b"+" + bytes_str + b"\r\n"


def bstring(string):
    bytes_str = bytes(string, encoding="utf-8")
    return b"$" + bytes(str(len(string)), encoding="utf-8") + b"\r\n" + bytes_str + b"\r\n"


def num(integer):
    return b":" + bytes(str(integer), encoding="utf-8") + b"\r\n"
