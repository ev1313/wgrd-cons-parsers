#!/usr/bin/env python3
import pdb
import sys
from cons_utils import *


def compress_ndfbin(data):
    header = Struct(
        "magic" / Magic(b"EUG0"),
        "magic2" / Int32ul,
        "magic3" / Magic(b"CNDF"),
        "compressed" / Enum(Int32ul, uncompressed=0x0, compressed=0x80),
        "toc0Offset" / Int32ul,
        "unk0" / Int32ul,
        "headerSize" / Int32ul,
        "unk2" / Int32ul,
        "size" / Int32ul,
        "unk4" / Int32ul,
        "uncompressedSize" / Int32ul,
        )
    parsed_ndfbin = header.parse(data)
    parsed_ndfbin.compressed = "compressed"
    parsed_ndfbin.uncompressedSize = len(data) - 40
    compressed_data = compress_zlib(data[40:], wbits=15)

    return header.build(parsed_ndfbin) + compressed_data


if __name__ == "__main__":
    f = open(sys.argv[1], "rb")
    data = f.read()

    compressed_data = compress_ndfbin(data)

    of1 = open(sys.argv[2], "wb")
    of1.write(compressed_data)
