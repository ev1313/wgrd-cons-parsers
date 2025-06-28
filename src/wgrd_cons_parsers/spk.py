#!/usr/bin/env python3

import pdb

import os
import sys
import argparse
import pathlib
from io import BytesIO

from conshex import *
from conshex.string import *
from conshex.lazy import *

from wgrd_cons_parsers.cons_utils import *

from wgrd_cons_parsers.common import *
from wgrd_cons_parsers.dictionary import *

EmptyHeader = Struct(
    "offset" / Int32ul,
    "size" / Int32ul,
)


def Header(subcon):
    H = Struct(
        "offset" / Int32ul,
        "size" / Int32ul,
        "data" / Area(subcon, offset=this.offset, size=this.size)
    )
    return H


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
        "data" / Area(subcon, offset=this.offset, size=this.size)
    )
    return HWC


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
    #"data" / Lazy(Pointer(this._._.ibufData.offset + this.offset, File(Bytes(this.size), lambda ctx: f"ibufs/ibuf_{ctx._index}_{ctx.offset}_{ctx.size}_{ctx.count}_{ctx.compressed}.bin")))
)

IbufDataHeader = Struct(
    "offset" / Int32ul,
    "size" / Int32ul,
    "data" / Array(lambda ctx: ctx._.ibufTable.count,
                   "ibufFile" / Struct("path" / Pointer(lambda ctx: ctx._.offset + ctx._._.ibufTable.data[ctx._index].offset,
                                        File(Bytes(lambda ctx: ctx._._.ibufTable.data[ctx._index].size),
                                             lambda ctx: f"ibufs/ibuf_{ctx._index}_{ctx._._.ibufTable.data[ctx._index].compressed}.bin")
                                        ))
                   ),
    )

VbufHeader = Struct(
    "offset" / Rebuild(Int32ul, lambda ctx: 0 if ctx._index == 0 else ctx._.data[ctx._index-1].offset + ctx._.data[ctx._index-1].size),
    "size" / Rebuild(Int32ul, this._data_meta._ptrsize),
    "count" / Int32ul,
    "vertexFormatIndex" / Int16ul,
    "compressed" / Enum(Int16ul, uncompressed=0x0, compressed=0xC000),
    #"data" / Lazy(Pointer(this._._.vbufData.offset + this.offset, File(Bytes(this.size), lambda ctx: f"vbufs/vbuf_{ctx._index}_{ctx.offset}_{ctx.size}_{ctx.count}_{ctx.compressed}.bin")))
)

VbufDataHeader = Struct(
    "offset" / Int32ul,
    "size" / Int32ul,
    "data" / Array(lambda ctx: ctx._.vbufTable.count,
                   "vbufFile" / Struct("path" / Pointer(lambda ctx: ctx._.offset + ctx._._.vbufTable.data[ctx._index].offset,
                                                        File(Bytes(lambda ctx: ctx._._.vbufTable.data[ctx._index].size),
                                                             lambda ctx: f"vbufs/vbuf_{ctx._index}_{ctx._._.vbufTable.data[ctx._index].compressed}.bin")
                                                        ))
                   ),
    )

NodeHeader = Struct(
    "offset" / Rebuild(Int32ul, lambda ctx: 0 if ctx._index == 0 else ctx._.data[ctx._index-1].offset + ctx._.data[ctx._index-1].size),
    "size" / Rebuild(Int32ul, this._data_meta._ptrsize),
    #"data" / Lazy(Pointer(this._._.nodesData.offset + this.offset, File(Bytes(this.size), lambda ctx: f"nodes/node_{ctx._index}_{ctx.offset}_{ctx.size}.bin")))
)

NodeDataHeader = Struct(
    "offset" / Int32ul,
    "size" / Int32ul,
    "data" / Array(lambda ctx: ctx._.nodesTable.count,
                   "nodeFile" / Struct("path" / Pointer(lambda ctx: ctx._.offset + ctx._._.nodesTable.data[ctx._index].offset,
                                                        File(Bytes(lambda ctx: ctx._._.nodesTable.data[ctx._index].size),
                                                             lambda ctx: f"nodes/node_{ctx._index}_{ctx._._.nodesTable.data[ctx._index].compressed}.bin")
                                                        ))
                   ),
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
    "unknown0" / HeaderWithCount(Unknown0, this._.materials.offset + this._.materials.size),
    "unknown1" / HeaderWithCount(Unknown1, this._.unknown0.offset + this._.unknown0.size),
    "meshes" / HeaderWithCount("Mesh" / Mesh, this._.unknown1.offset + this._.unknown1.size),
    "drawCalls" / HeaderWithCount("DrawCall" / DrawCall, this._.meshes.offset + this._.meshes.size),
    "ibufTable" / HeaderWithCount("Ibuf" / IbufHeader, this._.drawCalls.offset + this._.drawCalls.size),
    "ibufData" / IbufDataHeader,
    "vbufTable" / HeaderWithCount("Vbuf" / VbufHeader, this._.ibufTable.offset + this._.ibufTable.size),
    "vbufData" / VbufDataHeader,
    "nodesTable" / HeaderWithCount("Node" / NodeHeader, this._.vbufTable.offset + this._.vbufTable.size),
    "nodesData" / NodeDataHeader,
    "unknown10" / HeaderWithCount(Bytes(this.size), this._.nodesTable.offset + this._.nodesTable.size),
    "unknown10indices" / HeaderWithCount(Bytes(this.size), this._.unknown10.offset + this._.unknown10.size),
)

if __name__ == "__main__":
    main = CommonMain(Spk, "Spk")
    main.main()
