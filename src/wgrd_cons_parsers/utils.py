import ctypes
from io import BytesIO
import zlib
import os
from functools import partial


def debugPrint(s):
    if True:
        return
    print(s)


def remap(value, fromMin, fromMax, toMin, toMax):
    value01 = (value - fromMin) / (fromMax - fromMin)
    return value01 * (toMax - toMin) + toMin

def ctypes_is_int(T):
    return T in [ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint32, ctypes.c_int8, ctypes.c_int16, ctypes.c_int32]


def ctypes_is_float(T):
    return T in [ctypes.c_float, ctypes.c_double]


def read(f, T):
    data = f.read(ctypes.sizeof(T))
    return T.from_buffer_copy(data, 0)

def readb(f, T):
    data = f.read(ctypes.sizeof(T))
    return T.from_buffer_copy(data[::-1], 0)

def readItems(f, T, c):
    ret = []
    for i in range(c):
        ret.append(read(f, T))
    return ret


def printLoc(f, target):
    c = f.tell()
    print("%d / %d (%+d)" % (c, target, c - target))


def dumpBytes(path, d, output_folder="out/"):
    path = output_folder + path
    abspath = os.path.abspath(path)
    dirname = os.path.dirname(abspath)
    os.makedirs(dirname, exist_ok=True)
    o = open(path, "wb")
    o.write(d)


def dump(f, path, offset, size, output_folder="out/"):
    c = f.tell()
    f.seek(offset)
    d = f.read(size)
    dumpBytes(path, d, output_folder=output_folder)
    f.seek(c)
    return d


def assertLoc(f, target):
    printLoc(f, target)
    c = f.tell()
    assert (c == target)


def readMagic(f):
    return f.read(4)


def writeMagic(f, m):
    assert (len(m) == 4)
    f.write(m)


def readBytes(f, offset, size):
    f.seek(offset)
    d = f.read(size)
    return d

def read16sb(f):
    return readb(f, ctypes.c_int16).value

def read16b(f):
    return readb(f, ctypes.c_uint16).value

def read32b(f):
    return readb(f, ctypes.c_uint32).value

def read32sb(f):
    return readb(f, ctypes.c_int32).value

def read32(f):
    return read(f, ctypes.c_uint32).value


def read32s(f):
    return read(f, ctypes.c_int32).value


def read16(f):
    return read(f, ctypes.c_uint16).value


def read16s(f):
    return read(f, ctypes.c_int16).value


def read8(f):
    return read(f, ctypes.c_uint8).value


def read8s(f):
    return read(f, ctypes.c_int8).value


def readFloat(f):
    return read(f, ctypes.c_float).value


def readDouble(f):
    return read(f, ctypes.c_double).value


def encode8(v):
    return bytes(ctypes.c_uint8(v))


def encode8s(v):
    return bytes(ctypes.c_int8(v))


def encode16(v):
    return bytes(ctypes.c_uint16(v))


def encode16s(v):
    return bytes(ctypes.c_int16(v))


def encode32(v):
    return bytes(ctypes.c_uint32(v))


def encode32s(v):
    return bytes(ctypes.c_int32(v))


def encodeFloat(v):
    return bytes(ctypes.c_float(v))


def encodeDouble(f, v):
    return bytes(ctypes.c_double(v))


def write8(f, v):
    return f.write(encode8(v))


def write8s(f, v):
    return f.write(encode8s(v))


def write16(f, v):
    return f.write(encode16(v))

def write16s(f, v):
    return f.write(encode16s(v))

def write16b(f, v):
    return f.write(encode16(v)[::-1])

def write16sb(f, v):
    return f.write(encode16s(v)[::-1])


def write32(f, v):
    return f.write(encode32(v))

def write32s(f, v):
    return f.write(encode32s(v))

def write32b(f, v):
    return f.write(encode32(v)[::-1])

def write32sb(f, v):
    return f.write(encode32s(v)[::-1])


def writeFloat(f, v):
    return f.write(encodeFloat(v))


def writeDouble(f, v):
    return f.write(encodeDouble(v))


def align(v, n):
    p = (n - (v % n)) % n
    return v + p


def assertPad(b):
    assert(b == b"\x00" * len(b))

def readPad(f, v, n):
    p = align(v, n) - v
    d = f.read(p)
    assert (d == b'\x00' * p)


def writePad(f, v, n):
    p = align(v, n) - v
    d = f.write(b'\x00' * p)


def readString(f):
    s = b''
    while True:
        c = f.read(1)
        if c == b'\x00':
            break
        s += c
    return s


def readPaddedString(f, n):
    s = f.read(n)
    k = s.find(b'\x00')
    if k == -1:
        k = len(s)
    assert (s[k:] == b'\x00' * (n - k))
    return s[0:k]


def asciiSort(l):
    s = []

    def R(a, b):
        l = []
        for x in range(a[0], b[0] + 1):
            l += [bytes([x])]
        return l

    # Allowed symbols and their suspected precedence
    rank = [b'\\'] + [b'-'] + [b'.'] + R(b'0', b'9') + [b'_'] + R(b'a', b'z')

    # print(rank)
    for x in l:
        c = bytes([x])
        # print(c)
        assert (c in rank)
        s += [rank.index(c)]
    return s


def compress_zlib(data, level=9, wbits=15, depth=0):
    print("  " * depth + "compressing zlib data")
    d = data
    io = BytesIO(d)
    data = BytesIO()
    z = zlib.compressobj(level=level, wbits=wbits)
    for block in iter(partial(io.read, 8192), b''):
        data.write(z.compress(block))
    data.write(z.flush(zlib.Z_FULL_FLUSH))
    return bytes(data.getbuffer())


def decompress_zlib(data, wbits=0, depth=0):
    d = data
    fi = BytesIO(d)

    g = b''
    z = zlib.decompressobj(wbits)
    while True:
        buf = z.unconsumed_tail
        if buf == b"":
            buf = fi.read(8192)
            if buf == b"":
                break
        got = z.decompress(buf)
        if got == b"":
            break
        g += got
        # print(g)
    return g


def delta_encode(data, depth=0):
    print("  " * depth + "delta encoding data")
    input = data
    last = 0
    output = BytesIO()
    for block in iter(partial(input.read, 2), b''):
        current = int.from_bytes(block, "little")
        write16s(output, current - last)
        last = current
    return output.getbuffer()


def delta_decode(data, depth=0):
    print("  " * depth + "delta decoding data")
    input = data
    stream = BytesIO(input)
    last = 0
    output = BytesIO()
    for block in iter(partial(stream.read, 2), b''):
        last += int.from_bytes(block, "little")
        write16s(output, last)
    return output.getbuffer()


def writeString(f, s):
    f.write(s + b'\x00')


def readStringAlign(f, n):
    s = readString(f)
    readPad(f, len(s) + 1, n)
    return s


def writeStringAlign(f, n, s):
    writeString(f, s)
    writePad(f, len(s) + 1, n)


# Python `readlines` would keep newlines; naive `split` breaks for zero-length input
def loadLines(path):
    d = open(path, "rb").read()
    if len(d) == 0:
        return []
    return d.split(b'\n')


# Python `writelines` wouldn't include newlines
def dumpLines(path, lines):
    dumpBytes(path, b"\n".join(lines))
