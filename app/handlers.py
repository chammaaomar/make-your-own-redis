import threading
import time

import app.resp as RESP
import app.utils as utils

REDIS_DB = {}


def expire_key(key, ttl):
    time.sleep(ttl / 1000.0)
    del REDIS_DB[key]


def handle_ping(args):
    return RESP.bstring("PONG")


def handle_echo(args):
    return b"\r\n".join([*args, b""])


def handle_set(args):
    key = args[1]
    data_type = args[2][0]
    if data_type == RESP.INT:
        value = args[2][1:]
        REDIS_DB[key] = int(value, base=10)
        opt_indx = 3
    elif data_type == RESP.BSTRING:
        REDIS_DB[key] = str(args[3], encoding="utf-8")
        opt_indx = 4
    opts = [arg.upper() for arg in args[opt_indx:]]
    exp_indx = utils.safe_index(opts, RESP.PX)
    if exp_indx > -1:
        ttl = int(opts[exp_indx + 2], base=10)
        print(ttl)
        expiry_thread = threading.Thread(
            target=expire_key, args=(key, ttl))
        expiry_thread.start()
    return RESP.bstring("OK")


def handle_get(args):
    value = REDIS_DB.get(args[1], None)
    if value is None:
        return RESP.NIL
    if type(value) is int:
        return RESP.num(value)
    if type(value) is str:
        return RESP.bstring(value)
