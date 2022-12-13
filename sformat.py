#!/usr/bin/env python3

import sys
import pdb

from cons_utils import *
from cons_xml import *

SFormat = Struct(
    "unk0" / Const(0x06, Int8ul),
    "unk1" / Const(0x01, Int8ul),
    "isShort" / Enum(Int8ul, false=0, true=1),
    "channelCount" / Int8ul,
    "unk3" / Int16ul, # channelCount * 0x200
    "samplerate" / Int16ub,
    "frameCount" / Int32ul,
    "length" / Int32ul,
    "essLength" / Int32ul,
    "essUnk2" / Int32ul,
    "frameCount2" / Int32ul,
    "data" / If(lambda ctx: ctx.isShort == "false",
               Struct(
                   "unkCount" / Int32ul,
                   "unkX" / Int16ul,
                   "unkY" / Const(10, Int8ul),
                   "unkZ" / Const(5, Int8ul),
                   "data" / Bytes(lambda ctx: ctx._.length * 5),
                   )
               ),
    )

if __name__ == "__main__":
    f = open(sys.argv[1], "rb")
    data = f.read()

    d = SFormat.parse(data)