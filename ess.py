#!/usr/bin/env python3

from cons_utils import *
from cons_xml import *

from construct import *

from common import *

Ess = Struct(
    # FIXME: is this really a version number or maybe something else?
    "version" / Const(b"\x01\x00\x02\x02"),
    "isShort" / Enum(Int8ul, false=0, true=1),
    "channels" / Int8ul,
    "samplerate" / Int16ul,
    "frameCount" / Int32ub,
    "pad" / Const(b"\x00"*4),
    "samplecount2" / Int32ub,
    "sampleoffsets" / RepeatUntil(lambda obj,lst,ctx: obj == 0, Int32ub),
    "padding" / Const(b"\x00"*16),
    "framedata" / GreedyBytes,
)

if __name__ == "__main__":
    commonMain(Ess, "Ess")
