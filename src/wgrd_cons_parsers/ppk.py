#!/usr/bin/env python3

from .common import *

from dingsda import *
from dingsda.string import *

PPKTexture = Struct(
    "id" / Bytes(8),
    "offset" / Int32ul,
    "size" / Int32ul,
    "xea" / Int16ul,
    "xeb" / Int16ul,
    "xf" / Const(0, Int32ul),
    "tgvdata" / Pointer(lambda ctx: ctx.offset + ctx._.tex_offset, Bytes(lambda ctx: ctx.size)),
)

PPKPath = Struct(
    "path" / PaddedString(0x100, "utf-8"),
    "id" / Bytes(8),
)

PPK = Struct(
    "version" / Magic(b"PRXY"),
    "platform" / Magic(b"PCPC"),
    "unk0" / Const(8, Int32ul),
    "size" / Int32ul,
    "checksum" / Bytes(16),
    "unkBoffset" / Const(0x40, Int32ul),
    "unkBsize" / Int32ul,
    "tex_offset" / Rebuild(Int32ul, lambda ctx: ctx.unkBoffset + ctx.unkBsize),
    Check(lambda ctx: ctx.tex_offset == ctx.unkBoffset + ctx.unkBsize),
    "tex_size" / Int32ul,
    "tex_count" / Int32ul,
    "textures" / Area("Texture" / PPKTexture, this.unkBoffset, this.unkBsize),
    "paths_offset" / Rebuild(Int32ul, lambda ctx:ctx.tex_offset + ctx.tex_size),
    Check(lambda ctx: ctx.paths_offset == ctx.tex_offset + ctx.tex_size),
    "paths_size" / Int32ul,
    "paths_count" / Int32ul,
    Check(lambda ctx: ctx.paths_size == ctx.paths_count * (8+0x100)),
    Check(lambda ctx: ctx.paths_count == ctx.tex_count),
    "paths" / Area("Path" / PPKPath, this.paths_offset, this.paths_size),
    )


if __name__ == "__main__":
    main = CommonMain(PPK, "PPK")
    main.main()
