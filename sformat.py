#!/usr/bin/env python3

from cons_utils import *
from cons_xml import *

from common import *

SFormat = Struct(
    "unk0" / Const(0x06, Int8ul),
    "unk1" / Const(0x01, Int8ul),
    "isShort" / Enum(Int8ul, false=0, true=1),
    "channelCount" / Int8ul,
    "unk3" / Int16ul, # channelCount * 0x200
    "samplerate" / Int16ub,
    "frameCount" / Int32ul,
    "length" / Int32ul,
    "sformatLength" / Int32ul,
    "sformatUnk2" / Int32ul,
    "frameCount2" / Int32ul,
    "data" / If(lambda ctx: ctx.isShort == "false",
               Struct(
                   "unkCount" / Int32ul,
                   "unkX" / Int16ul,
                   "unkY" / Const(10, Int8ul),
                   "unkZ" / Const(5, Int8ul),
                   "data" / Array(this.unkCount, "item" / Struct("data" / Array(5, Int8ul))),
                   )
               ),
    )

if __name__ == "__main__":
    commonMain(SFormat, "SFormat")
