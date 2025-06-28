#!/usr/bin/env python3

import sys
import pdb
from conshex import *
from wgrd_cons_parsers.cons_utils import decompress_zlib


def decompress_ndfbin(data, update_header=False):
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
    parsed_header = header.parse(data)

    if update_header:
        parsed_header.compressed = "uncompressed"

    if parsed_header["compressed"] == "compressed":
        uncompressed_data = data[:40] + decompress_zlib(data[44:])
        print("Uncompressed")
    else:
        uncompressed_data = data
        print("Copied")
    return uncompressed_data


if __name__ == "__main__":
    f = open(sys.argv[1], "rb")
    data = f.read()

    uncompressed_data = decompress_ndfbin(data)

    of1 = open(sys.argv[2], "wb")
    of1.write(uncompressed_data)
    print("Wrote to %s" % sys.argv[2])
