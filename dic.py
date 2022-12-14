#!/usr/bin/env python3

import pdb

import os
import sys
import argparse
import pathlib
from io import BytesIO

from cons_utils import *
from cons_xml import *

from common import *


Dic = Struct(
    "magic" / Const(b"TRAD"),
    "count" / Rebuild(Int32ul, len_(this.entries)),
    "entries" / Array(this.count, "Entry" / Struct(
        "hash" / Int64ul,
        "offset" / Rebuild(Int32ul, lambda ctx: ctx._._endoffset_entries + sum([x["_ptrsize_string"] for x in ctx._.entries[0:ctx._index]])),
        "length" / Rebuild(Int32ul, lambda ctx: len(ctx.string)),
        "string" / Pointer(this.offset, PaddedString(this.length*2, "utf-16-le")),
    )),
)


if __name__ == "__main__":
    #FIXME: add extra options to respect extra arguments
    commonMain(Dic, "Dic")
