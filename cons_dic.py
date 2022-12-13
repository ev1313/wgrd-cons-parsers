#!/usr/bin/env python3

import pdb

import os
import sys
from io import BytesIO

from cons_utils import *
from cons_xml import *

Dic = Struct(
    "magic" / Const(b"TRAD"),
    "count" / Rebuild(Int32ul, len_(this.entries)),
    "entries" / Array(this.count, "Entry" / Struct(
        "hash" / Int64ul,
        "offset" / Rebuild(Int32ul, lambda ctx: (8+len(ctx._.entries) * 16) if ctx._index == 0 else (8+len(ctx._.entries) * 16) + sum([len(x.string)*2 for x in ctx._.entries[0:ctx._index]])),
        "length" / Rebuild(Int32ul, lambda ctx: len(ctx.string)),
        "string" / Pointer(this.offset, PaddedString(this.length*2, "utf-16-le")),
    )),
)


if __name__ == "__main__":
    f = open(sys.argv[1], "rb")
    data = f.read()

    dic = Dic.parse(data)
    xml = Dic.toET(dic, name="Dic", is_root=True)
    sys.stderr.write("indenting xml...\n")
    ET.indent(xml, space="  ", level=0)
    sys.stderr.write("finished indenting xml...\n")
    str = ET.tostring(xml).decode("utf-8")
    sys.stderr.write("finished generating xml...\n")
    f = open("out/dic.xml", "wb")
    f.write(str.encode("utf-8"))
    f.close()
    print(str)

    sys.stderr.write("test building xml...\n")
    x = Dic.fromET(xml, "Dic", is_root=True)
    sys.stderr.write("built test xml...\n")

    rebuild = Dic.build(x)

    f = open("out/dic.dic", "wb")
    f.write(rebuild)
    f.close()

    assert(rebuild == data)
