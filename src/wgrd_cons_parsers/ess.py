#!/usr/bin/env python3

from conshex import *

from wgrd_cons_parsers.common import *

Ess = Struct(
    # FIXME: is this really a version number or maybe something else?
    "version" / Const(b"\x01\x00\x02\x02"),
    "isShort" / Enum(Int8ub, false=0, true=1),
    "channels" / Int8ub,
    "samplerate" / Int16ub,
    "frameCount" / Int32ub,
    "loopStart" / Int32ub,
    "loopEnd" / Int32ub,
    "blockOffsets" / RepeatUntil(lambda obj,lst,ctx: obj == 0, Int32ub),
    "padding" / Const(b"\x00"*16),
    "blockData" / GreedyBytes,
)

if __name__ == "__main__":
    main = CommonMain(Ess, "Ess")
    main.main()
