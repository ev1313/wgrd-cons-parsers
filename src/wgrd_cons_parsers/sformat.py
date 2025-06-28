#!/usr/bin/env python3

from conshex import *

from wgrd_cons_parsers.common import *


SFormat = Struct(
    "unk0" / Enum(Int8ul, wgrd=0x06, warno=0x0),
    "unk1" / Const(0x01, Int8ul),
    "isShort" / Enum(Int8ul, false=0, true=1),
    "channelCount" / Int8ul,
    "frameSize" / Int16ul, # channelCount * 0x200
    "sampleRate" / Int16ul,
    "frameCount" / Int32ul,
    "unk4" / Int32ul,
    "essLength" / Int32ul,
    "loopStart" / Int32ul,
    "loopEnd" / Int32ul,
    "data" / If(lambda ctx: ctx.isShort == "false",
               Struct(
                   "unkCount" / Int32ul,
                   "unkX" / Int16ul,
                   "unkY" / Const(10, Int8ul),
                   "unkZ" / Const(5, Int8ul),
                   "data" / Array(this.unkCount, "item" / Struct("data" / Array(5, Int8ul))),
                   )
               )
    )


if __name__ == "__main__":
    main = CommonMain(SFormat, "SFormat")
    main.main()
