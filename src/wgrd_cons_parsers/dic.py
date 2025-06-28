#!/usr/bin/env python3

from wgrd_cons_parsers.common import *

from conshex import *
from conshex.string import *

Dic = Struct(
    "magic" / Const(b"TRAD"),
    "count" / Rebuild(Int32ul, len_(this.entries)),
    "entries" / Array(this.count, "Entry" / Struct(
        "hash" / Bytes(8),
        "offset" / Rebuild(Int32ul, lambda ctx: ctx._._entries_meta._endoffset + sum([x._string_meta._ptr_size for x in ctx._.entries[0:ctx._index]])),
        "length" / Rebuild(Int32ul, lambda ctx: len(ctx.string)),
        "string" / Pointer(this.offset, PaddedString(this.length*2, "utf-16-le")),
    )),
)


if __name__ == "__main__":
    main = CommonMain(Dic, "Dic")
    main.main()
