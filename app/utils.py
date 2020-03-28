import app.resp as RESP


def bad_cmd_format(cmd_tokens):
    """
    Checks if request is RESP-compliant. Should be an array of bulk strings
    """
    try:
        array_spec = cmd_tokens[0][0]
        array_spec_num_elems = int(cmd_tokens[0][1:], base=10)
        num_elements = 0
        if array_spec != RESP.ARRAY:
            return True
        for index, token in enumerate(cmd_tokens[1:]):
            if token[0] == RESP.BSTRING:
                string_spec = token
                string = cmd_tokens[index + 2]
                if bad_string_format(string_spec, string):
                    return True
                num_elements += 1
            if token[0] == RESP.INT:
                num = token[1:]
                if not num.isdigit():
                    return True
                num_elements += 1
            if token[0] == RESP.SSTRING:
                num_elements += 1
        return array_spec_num_elems != num_elements
    except IndexError:
        return True


def bad_string_format(string_spec, string):
    str_len = int(string_spec[1:], base=10)
    return str_len != len(string)


def error(conn, msg):
    res = bytes(f"-{msg}\r\n", "utf-8")
    conn.sendall(res)
    return


def safe_index(array, item):
    try:
        return array.index(item)
    except ValueError:
        return - 1
