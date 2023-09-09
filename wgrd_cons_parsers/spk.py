#!/usr/bin/env python3

import pdb

import os
import sys
import argparse
import pathlib
from io import BytesIO

from dingsda import *
from dingsda.string import *
from dingsda.lazy import *

from cons_utils import *

from .common import *
from .dictionary import *

EmptyHeader = Struct(
    "offset" / Int32ul,
    "size" / Int32ul,
)


def Header(subcon):
    H = Struct(
        "offset" / Int32ul,
        "size" / Int32ul,
        "data" / Pointer(this.offset, subcon),
    )
    return EmptyHeader


EmptyHeaderWithCount = Struct(
    "offset" / Int32ul,
    "size" / Int32ul,
    "count" / Int32ul,
)


def HeaderWithCount(subcon, offset):
    HWC = Struct(
        "offset" / Rebuild(Int32ul, offset),
        "size" / Rebuild(Int32ul, this._data_meta._ptrsize),
        "count" / Rebuild(Int32ul, len_(this.data)),
        "data" / Pointer(this.offset, subcon)
    )
    return EmptyHeaderWithCount


FileItem = Struct(
    "minX" / Float32l,
    "minY" / Float32l,
    "minZ" / Float32l,
    "maxX" / Float32l,
    "maxY" / Float32l,
    "maxZ" / Float32l,
    "flags" / Int32ul,
    Check(lambda ctx: ctx.flags in [0x0, 0x1]),
    "meshIndex" / Int16ul,
    "nodesIndex" / Int16ul,
)

VertexFormat = Struct(
    "length" / Int32ul,
    "formats" / Array(this._.count, "VertexFormat" / Struct("name" / PaddedString(this._.length, "utf-8")))
)

VertexFormatHeader = Struct(
    "offset" / Rebuild(Int32ul, this._.files.offset + this._.files.size),
    "size" / Rebuild(Int32ul, this._data_meta._ptrsize),
    "count" / Rebuild(Int32ul, len_(this.data.formats)),
    "data" / Pointer(this.offset, VertexFormat)
)

Unknown0 = Struct(
    "minX" / Float32l,
    "minY" / Float32l,
    "minZ" / Float32l,
    "maxX" / Float32l,
    "maxY" / Float32l,
    "maxZ" / Float32l,
    "unk6aSomeIndex" / Int16ul,
    "cdcd" / Const(b"\xcd\xcd"),
    "unk7OffsetOrIndex" / Int32ul,
    "unk7SizeOrCount" / Int32ul,
    "unk9OffsetOrIndex" / Int32ul,
    "unk9SizeOrCount" / Int32ul,
    "unk11" / Int8ul,
    "cdcdcd" / Const(b"\xcd\xcd\xcd"),
)

Unknown1 = Struct(
    "unknownIndex" / Int32ul,
    "count" / Int32ul,
)

Mesh = Struct(
    "drawCallIndex" / Int16ul,
    "count" / Int16ul,
    )

DrawCall = Struct(
    "fileIndex" / Int16ul,
    "materialIndex" / Int16ul,
    "ibufTableIndex" / Int16ul,
    "vbufTableIndex" / Int16ul,
    "unk0" / Int16ul,
    "unk1" / Const(0xCDCD, Int16ul),
)

IbufHeader = Struct(
    "offset" / Rebuild(Int32ul, lambda ctx: 0 if ctx._index == 0 else ctx._.data[ctx._index-1].offset + ctx._.data[ctx._index-1].size),
    "size" / Rebuild(Int32ul, this._data_meta._ptrsize),
    "count" / Int32ul,
    "unk1" / Const(0x1, Int16ul),
    "compressed" / Enum(Int16ul, uncompressed=0x0, compressed=0xC000),
    "data" / Lazy(Pointer(this._._.ibufData.offset + this.offset, File(Bytes(this.size), lambda ctx: f"ibufs/ibuf_{ctx._index}_{ctx.offset}_{ctx.size}_{ctx.count}_{ctx.compressed}.bin")))
)

VbufHeader = Struct(
    "offset" / Rebuild(Int32ul, lambda ctx: 0 if ctx._index == 0 else ctx._.data[ctx._index-1].offset + ctx._.data[ctx._index-1].size),
    "size" / Rebuild(Int32ul, this._data_meta._ptrsize),
    "count" / Int32ul,
    "vertexFormatIndex" / Int16ul,
    "compressed" / Enum(Int16ul, uncompressed=0x0, compressed=0xC000),
    "data" / Lazy(Pointer(this._._.vbufData.offset + this.offset, File(Bytes(this.size), lambda ctx: f"vbufs/vbuf_{ctx._index}_{ctx.offset}_{ctx.size}_{ctx.count}_{ctx.compressed}.bin")))
)

NodeHeader = Struct(
    "offset" / Rebuild(Int32ul, lambda ctx: 0 if ctx._index == 0 else ctx._.data[ctx._index-1].offset + ctx._.data[ctx._index-1].size),
    "size" / Rebuild(Int32ul, this._data_meta._ptrsize),
    "data" / Lazy(Pointer(this._._.nodesData.offset + this.offset, File(Bytes(this.size), lambda ctx: f"nodes/node_{ctx._index}_{ctx.offset}_{ctx.size}.bin")))
)

Spk = Struct(
    "typeMagic" / Const(b"MESH"),
    "platformMagic" / Const(b"PCPC"),
    "version" / Const(7, Int32ul),
    "fileSize" / Int32ul,
    "checksum" / Bytes(16),
    "block1" / EmptyHeader,
    "block2" / EmptyHeaderWithCount,
    "files" / HeaderWithCount(Dictionary("FileItem" / FileItem, this.offset, this.size), this._._endoffset_unknown10indices),
    "vertexFormats" / VertexFormatHeader,
    "materials" / HeaderWithCount(File(Bytes(this.size), lambda ctx: "materials.ndfbin"), this._.vertexFormats.offset + this._.vertexFormats.size),
    "unknown0" / HeaderWithCount(Array(this.count, Unknown0), this._.materials.offset + this._.materials.size),
    "unknown1" / HeaderWithCount(Array(this.count, Unknown1), this._.unknown0.offset + this._.unknown0.size),
    "meshes" / HeaderWithCount(Array(this.count, "Mesh" / Mesh), this._.unknown1.offset + this._.unknown1.size),
    "drawCalls" / HeaderWithCount(Array(this.count, "DrawCall" / DrawCall), this._.meshes.offset + this._.meshes.size),
    "ibufTable" / HeaderWithCount(Array(this.count, "Ibuf" / IbufHeader), this._.drawCalls.offset + this._.drawCalls.size),
    "ibufData" / EmptyHeader,
    "vbufTable" / HeaderWithCount(Array(this.count, "Vbuf" / VbufHeader), this._.ibufTable.offset + this._.ibufTable.size),
    "vbufData" / EmptyHeader,
    "nodesTable" / HeaderWithCount(Array(this.count, "Node" / NodeHeader), this._.vbufTable.offset + this._.vbufTable.size),
    "nodesData" / EmptyHeader,
    "unknown10" / HeaderWithCount(Bytes(this.size), this._.nodesTable.offset + this._.nodesTable.size),
    "unknown10indices" / HeaderWithCount(Bytes(this.size), this._.unknown10.offset + this._.unknown10.size),
)

if __name__ == "__main__":
    main = CommonMain(Spk, "Spk")
    main.main()
