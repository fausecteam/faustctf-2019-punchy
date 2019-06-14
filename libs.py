from ctypes import CDLL, POINTER, c_char_p, c_void_p, c_int, pointer, create_string_buffer, cast, c_char

lib_decode = CDLL('extensions/decode/decode.so')

list_encodings = lib_decode.ListEncodingsExport
list_encodings.restype = POINTER(c_char_p)

free_encodings = lib_decode.FreeEncodings
check_encoding = lib_decode.CheckEncodingExport

decode = lib_decode.DecodeExport
decode.argtypes = [c_char_p, (c_int*80)]
decode.restype = c_char_p

check_encoding()

lib_join = CDLL('extensions/join/join.so')

join_cmds = lib_join.join_commands
join_cmds.argtypes = [POINTER(c_char_p), c_int]
join_cmds.restype = c_void_p

free_memory = lib_join.free_memory
free_memory.argtypes = [c_void_p]


def get_encodings():
    l = list_encodings()
    i = 0
    res = list()
    while l[i]:
        res.append(l[i].decode('ascii'))
        i += 1
    free_encodings(l)
    return res

def decode_card(encoding, card):
    x = (c_int*80)(*card)
    d = decode(create_string_buffer(encoding), x)
    return d


def join_commands(lines):
    cmds = (c_char_p * len(lines))()
    cmds[:] = lines

    r = join_cmds(cmds, len(lines))
    cmd = (cast(r, c_char_p).value).decode('ascii')
    free_memory(r)
    return cmd

lib_staply = CDLL('extensions/staply/libstaply.so')

init_func = lib_staply.init_staply
init_func()

check_help_func = lib_staply.check_for_possible_help
check_help_func.argtypes = [c_char_p]
check_help_func.restype  = c_char_p

run_help_func = lib_staply.run_help
run_help_func.argtypes = [c_char_p]
run_help_func.restype  = POINTER(c_char)

def check_help(data):
    ret = check_help_func(data)
    if ret is None:
        return None
    else:
        return ret.decode('ascii')

def run_help(data):
    help = run_help_func(data)
    ret = (cast(help, c_char_p).value).decode('latin1')
    return ret
