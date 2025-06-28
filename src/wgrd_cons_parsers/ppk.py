#!/usr/bin/env python3

from wgrd_cons_parsers.common import *
from wgrd_cons_parsers.cons_utils import *

from conshex import *
from conshex.helpers import *
from conshex.string import *

PPKTexture = Struct(
    "id" / Bytes(8),
    "offset" / Rebuild(Int32ul, lambda ctx: sum([x.size for x in ctx._.textures[0:ctx._index]])),
    "size" / Rebuild(Int32ul, lambda ctx: len(ctx.tgvdata)),
    "xea" / Int16ul,
    "xeb" / Int16ul,
    "xf" / Const(0, Int32ul),
    "tgvdata" / Pointer(lambda ctx: ctx.offset + ctx._.tex_offset, File(Bytes(lambda ctx: ctx.size), lambda ctx: f"ppk/{ctx.id}_{ctx.xea}_{ctx.xeb}_{ctx.xf}.tgv")),
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
    "unkBsize" / Rebuild(Int32ul, lambda ctx: 24*len(ctx.textures)),
    "tex_offset" / Rebuild(Int32ul, lambda ctx: ctx.unkBoffset + ctx.unkBsize),
    Check(lambda ctx: ctx.tex_offset == ctx.unkBoffset + ctx.unkBsize),
    "tex_size" / Rebuild(Int32ul, lambda ctx: sum([x.size for x in ctx.textures])),
    "tex_count" / Rebuild(Int32ul, lambda ctx: len(ctx.textures)),
    "textures" / Area("Texture" / PPKTexture, this.unkBoffset, this.unkBsize),
    "paths_offset" / Rebuild(Int32ul, lambda ctx:ctx.tex_offset + ctx.tex_size),
    Check(lambda ctx: ctx.paths_offset == ctx.tex_offset + ctx.tex_size),
    "paths_size" / Rebuild(Int32ul, lambda ctx: ctx.paths_count * (8+0x100)),
    "paths_count" / Rebuild(Int32ul, this.tex_count),
    Check(lambda ctx: ctx.paths_size == ctx.paths_count * (8+0x100)),
    Check(lambda ctx: ctx.paths_count == ctx.tex_count),
    "paths" / Area("Path" / PPKPath, this.paths_offset, this.paths_size),
    )


if __name__ == "__main__":
    main = CommonMain(PPK, "PPK")
    main.main()
