#!/usr/bin/env python3

import pdb

import os
import sys
from io import BytesIO

from utils import decompress_zlib
import xml.etree.ElementTree as ET

from construct import *

EssHeader = Struct(
    # FIXME: is this really a version number or maybe something else?
    "version" / Const(b"\x01\x00\x02\x02"),
    # apparently always 0 or 1
    "unk" / Enum(Int8ul, false=0, true=1),
    "channels" / Int8ul,
    "samplerate" / Int16ul,
    "frameCount" / Int32ub,
    "pad" / Const(b"\x00"*4),
    "samplecount2" / Int32ub,
    "sampleoffsets" / RepeatUntil(lambda obj,lst,ctx: obj == 0, Int32ub),
    "padding" / Const(b"\x00"*16),
)

if __name__ == "__main__":
    f = open(sys.argv[1], "rb")
    data = f.read()

    header = EssHeader.parse(data)
    print(header)

    frames = []
    old = 0
    for offset in header["sampleoffsets"]:
        frame = data[old:offset]
        frames.append(frame)
        old = offset
        print(frame)