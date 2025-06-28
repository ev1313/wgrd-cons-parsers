#!/usr/bin/env python3
import pdb
import sys
from conshex import *

from wgrd_cons_parsers.cons_utils import *

def compress_ndfbin(data, update_header=False):
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

    if update_header:
        parsed_ndfbin.compressed = "compressed"

    # FIXME: hardcoded values for WGRD
    parsed_ndfbin.toc0Offset = len(data) - 224
    parsed_ndfbin.size = len(data)
    parsed_ndfbin.uncompressedSize = len(data) - 40

    if parsed_ndfbin.compressed == "compressed":
        compressed_data = compress_zlib(data[40:], wbits=15)

        return header.build(parsed_ndfbin) + compressed_data
    else:
        return data


if __name__ == "__main__":
    f = open(sys.argv[1], "rb")
    data = f.read()

    compressed_data = compress_ndfbin(data)

    of1 = open(sys.argv[2], "wb")
    of1.write(compressed_data)
