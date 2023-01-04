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
from dictionary import *

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
    return H


EmptyHeaderWithCount = Struct(
    "offset" / Int32ul,
    "size" / Int32ul,
    "count" / Int32ul,
)


def HeaderWithCount(subcon, offset):
    HWC = Struct(
        "offset" / Rebuild(Int32ul, offset),
        "size" / Rebuild(Int32ul, this._ptrsize_data),
        "count" / Rebuild(Int32ul, len_(this.data)),
        "data" / Pointer(this.offset, subcon)
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
    "offset" / Rebuild(Int32ul, this._._offset_files + this._._size_files),
    "size" / Rebuild(Int32ul, this._ptrsize_data),
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
    "offset" / Int32ul,
    "size" / Int32ul,
    "count" / Int32ul,
    "unk1" / Const(0x1, Int16ul),
    "compressed" / Enum(Int16ul, uncompressed=0x0, compressed=0xC000),
)

VbufHeader = Struct(
    "offset" / Int32ul,
    "size" / Int32ul,
    "count" / Int32ul,
    "vertexFormatIndex" / Int16ul,
    "compressed" / Enum(Int16ul, uncompressed=0x0, compressed=0xC000),
)

NodeHeader = Struct(
    "offset" / Int32ul,
    "size" / Int32ul,
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
    "materials" / HeaderWithCount(Bytes(this.size), this._._offset_vertexFormats + this._._size_vertexFormats),
    "unknown0" / HeaderWithCount(Array(this.count, Unknown0), lambda ctx: 0),
    "unknown1" / HeaderWithCount(Array(this.count, Unknown1), lambda ctx: 0),
    "meshes" / HeaderWithCount(Array(this.count, "Mesh" / Mesh), this._._offset_materials + this._._size_materials),
    "drawCalls" / HeaderWithCount(Array(this.count, "DrawCall" / DrawCall), this._._offset_meshes + this._._size_meshes),
    "ibufTable" / HeaderWithCount(Array(this.count, "Ibuf" / IbufHeader), this._._offset_drawCalls + this._._size_drawCalls),
    "ibufData" / Header(Bytes(this.size)),
    "vbufTable" / HeaderWithCount(Array(this.count, "Vbuf" / VbufHeader), this._._offset_ibufTable + this._._size_ibufTable),
    "vbufData" / Header(Bytes(this.size)),
    "nodesTable" / HeaderWithCount(Array(this.count, "Node" / NodeHeader), lambda ctx: 0),
    "nodesData" / Header(Bytes(this.size)),
    "unknown10" / HeaderWithCount(Bytes(this.size), lambda ctx: 0),
    "unknown10indices" / HeaderWithCount(Bytes(this.size), lambda ctx: 0),
    Probe(),
)

if __name__ == "__main__":
    commonMain(Spk, "Spk")
