#!/usr/bin/env python3

from .common import *

from dingsda import *
from dingsda.string import *

from .utils import align

TGV = Struct(
    "version" / Int32ul,
    "compressed" / Int32ul,
    "width" / Int32ul,
    "height" / Int32ul,
    "imageWidth" / Int32ul,
    "imageHeight" / Int32ul,
    "mipmapCount" / Rebuild(Int16ul, lambda ctx: len(ctx.images)),
    "pixelFormatName" / Aligned(7, PascalString(Int16ul, "utf-8")),
    "checksum" / Bytes(16),
    "offsets" / Rebuild(Array(this.mipmapCount, Int32ul), lambda ctx: [ctx._checksum_meta._endoffset + 2*ctx.mipmapCount*4 + sum([align(s, 4) for s in ctx.sizes[0:x]]) for x in range(ctx.mipmapCount)]),
    "sizes" / Rebuild(Array(this.mipmapCount, Int32ul), lambda ctx: [len(ctx.images[x].data) for x in range(ctx.mipmapCount)]),
    "images" / Array(this.mipmapCount, "mipmap" / Pointer(lambda ctx: ctx.offsets[ctx._index], Struct("data" / Aligned(4, Bytes(lambda ctx: ctx._.sizes[ctx._._index]))))),
    )


if __name__ == "__main__":
    main = CommonMain(TGV, "TGV")
    main.main()
