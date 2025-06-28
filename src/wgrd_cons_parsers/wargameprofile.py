#!/usr/bin/env python3

import pdb

from conshex import *
from conshex.lib import *
from wgrd_cons_parsers.cons_utils import *
from wgrd_cons_parsers.common import CommonMain

WargameProfile = Struct(
    "magic" / Magic(b"ESAV"),
    "unk0" / Const(1, Int32ub),
    "length" / Int32ub,
    "x" / Array(28, Byte),
    "asd" / Int32ub, # static across multiple files
    "x0" / Int32ul,
    "x1" / Int32ub,
    "x2" / Int32ul,
    "unk1" / Int32ub, # maybe version, not different across different profiles
    "timestamp" / Int32ul,
    "y0" / Int32ul,
    "sama" / Magic(b"\x00" * 28 + b"\xFF" * 8 + b"\x00" * 10 + b"sama" + b"\x00" * 4),
    "restlength" / Int32ub,
    "w1" / Const(0, Int32ul),
    "w2" / Const(1, Int32ul),
    "profile" / PascalString(Int32ul, "ascii"),
    "ndflength" / Int32ul,
    "ndf" / File(Bytes(this.ndflength), "profile.ndfbin"),
)

if __name__ == "__main__":
    main = CommonMain(WargameProfile, "WargameProfile")
    main.main()
