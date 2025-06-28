#!/usr/bin/env python3

from conshex import *

from wgrd_cons_parsers.common import *
from wgrd_cons_parsers.cons_utils import decompress_zlib

import os

import argparse

XYZ = Struct(
    # FIXME: is this really a version number or maybe something else?
    "version" / Const(b"XYZ0"),
    "pyHeader" / Bytes(4),
    "uncompressedLength" / Int32ul,
    "checksum" / Bytes(16),
    "blockData" / GreedyBytes,
)
def decompress_xyz(data):
    header = Struct(
    "version" / Const(b"XYZ0"),
    "pyHeader" / Bytes(4),
    "uncompressedLength" / Int32ul,
    "checksum" / Bytes(16),
    "data" / GreedyBytes,
    )
    parsed_header = header.parse(data)

    uncompressed_data = decompress_zlib(parsed_header["data"])
    header = parsed_header["pyHeader"][::-1]
    timestamp = b"\x00\x00\x00\x00"
    return header + timestamp + uncompressed_data

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Decompress XYZ files")
    argparser.add_argument("inputs", help="Input XYZ file(s)", nargs="+")
    argparser.add_argument("-o", default="out/", help="Output file")
    args = argparser.parse_args()

    for input in args.inputs:
        with open(input, "rb") as f:
            data = f.read()

        uncompressed_data = decompress_xyz(data)

        with open(args.o + os.path.basename(input) + ".pyc", "wb") as f:
            f.write(uncompressed_data)
            print(f"Wrote to {args.o}")

