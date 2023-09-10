#!/usr/bin/env python3

import pdb

import os
import sys
import argparse
import pathlib
from io import BytesIO

from dingsda import *
from dingsda.string import PascalString
from dingsda.lazy import LazyBound

from .cons_utils import *

from .compress_ndfbin import compress_ndfbin
from .decompress_ndfbin import decompress_ndfbin

from .common import CommonMain

NDFType = Struct(
    "typeId" / Rebuild(Int32ul, this._switch_id_data),
    "data" / Switch(this.typeId, {
        0x00000000: "Boolean" / Struct("value" / Enum(Int8ul, false=0, true=1)),
        0x00000001: "Int8" / Struct("value" / Int8ul),
        0x00000002: "Int32" / Struct("value" / Int32sl),
        0x00000003: "UInt32" / Struct("value" / Int32ul),
        0x00000005: "Float32" / Struct("value" / Float32l),
        0x00000006: "Float64" / Struct("value" / Float64l),
        0x00000007: "StringReference" / Struct("stringIndex" / Int32ul),
        0x00000008: "WideString" / Struct("str" / PascalString(Int32ul, "utf-16-le")),
        0x00000009: "Reference" / Struct(
            "typeId" / Rebuild(Int32ul, this._switch_id_ref),
            "ref" / Switch(this.typeId, {
                0xAAAAAAAA: "TranReference" / Struct("tranIndex" / Int32ul),
                0xBBBBBBBB: "ObjectReference" / Struct(
                    "objectIndex" / Int32ul,
                    "classIndex" / Int32ul,
                ),
            }),
        ),
        0x0000000B: "F32_vec3" / Struct("x" / Float32l, "y" / Float32l, "z" / Float32l),
        0x0000000C: "F32_vec4" / Struct("x" / Float32l, "y" / Float32l, "z" / Float32l, "w" / Float32l),
        0x0000000D: "Color" / Struct("r" / Int8ul, "g" / Int8ul, "b" / Int8ul, "a" / Int8ul),
        0x0000000E: "S32_vec3" / Struct("x" / Int32sl, "y" / Int32sl, "z" / Int32sl),
        0x0000000F: "Matrix" / Struct("Matrix" / Array(16, Float32l)),
        0x00000011: "List" / Struct("length" / Rebuild(Int32ul, len_(this.items)), "items" / LazyBound(lambda: NDFType)[this.length]),
        0x00000012: "Map" / Struct(
            "count" / Rebuild(Int32ul, len_(this.mapitem)),
            "mapitem" / Struct(
                "key" / LazyBound(lambda: NDFType),
                "value" / LazyBound(lambda: NDFType),
            )[this.count]),
        0x00000013: "Long" / Struct("value" / Int64ul),
        0x00000014: "Blob" / Struct(
            "size" / Int32ul,
            "data" / Bytes(this.size),
        ),
        0x00000018: "S16" / Struct("value" / Int16sl),
        0x00000019: "U16" / Struct("value" / Int16ul),
        0x0000001A: "GUID" / Struct("data" / Bytes(16)),
        0x0000001C: "PathReference" / Struct("stringIndex" / Int32ul),
        0x0000001D: "LocalisationHash" / Struct("data" / Bytes(8)),
        0x0000001E: "UnknownBlob" / Struct(  # StringBlob?
            "size" / Int32ul,
            "unk0" / Int8ul,  # Const(b'\x01'),
            "data" / Switch(this.unk0, {
                0: "Raw" / Struct(
                    "data" / Bytes(this._.size)
                ),
                1: "Zlib" / Struct(
                    "uncompressedSize" / Int32ul,
                    # FIXME: Zero pad output of ZlibCompressed to `uncompressedSize`
                    "data" / ZlibCompressed(Bytes(this._.size - 4)),
                )
            })
        ),
        0x00000022: "Pair" / Struct(
            "first" / LazyBound(lambda: NDFType),
            "second" / LazyBound(lambda: NDFType),
        ),
        0x0000001F: "S32_vec2" / Struct("x" / Int32sl, "y" / Int32sl),
        0x00000021: "F32_vec2" / Struct("x" / Float32l, "y" / Float32l),
        0x00000025: "Hash" / Struct("hash" / Bytes(16)),
    }, default=Error),
)

NDFProperty = Struct(
    "propertyIndex" / Int32ul,
    "value" / If(lambda ctx: ctx.propertyIndex != 0xABABABAB, NDFType),
)

NDFObject = Struct(
    "classIndex" / Int32ul,
    "properties" / RepeatUntil(lambda obj, lst, ctx: obj.propertyIndex == 0xABABABAB, "Property" / NDFProperty),
)

# generic table
TOC0Table = Struct(
    "magic" / Bytes(4),
    "pad0" / Const(b"\x00" * 4),
    "offset" / Int32ul,
    "pad1" / Const(b"\x00" * 4),
    "size" / Int32ul,
    "pad2" / Const(b"\x00" * 4),
)

# first table
OBJETable = Struct(
    "magic" / Magic(b"OBJE"),
    "pad0" / Const(b"\x00" * 4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._._.headerSize),
    "pad1" / Const(b"\x00" * 4),
    "size" / Rebuild(Int32ul, lambda foo: foo._objects_meta._ptrsize),
    "pad2" / Const(b"\x00" * 4),
    "objects" / Area("Object" / NDFObject, offset=this.offset, size=this.size),
)

# second table
TOPOTable = Struct(
    "magic" / Magic(b"TOPO"),
    "pad0" / Const(b"\x00" * 4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._.OBJE.offset + foo._.OBJE._objects_meta._ptrsize),
    "pad1" / Const(b"\x00" * 4),
    "size" / Rebuild(Int32ul, lambda foo: foo._topobjects_meta._ptrsize),
    "pad2" / Const(b"\x00" * 4),
    "topobjects" / Area("TopObject" / Struct(
        "objectIndex" / Int32ul,
    ), offset=this.offset, size=this.size),
)

# third table
CHNKTable = Struct(
    "magic" / Magic(b"CHNK"),
    "pad0" / Const(b"\x00" * 4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._.TOPO.offset + foo._.TOPO._topobjects_meta._ptrsize),
    "pad1" / Const(b"\x00" * 4),
    "size" / Rebuild(Int32ul, lambda foo: foo._chunks_meta._ptrsize),
    "pad2" / Const(b"\x00" * 4),
    # FIXME: check if unk0 is topOfObjectIndex
    "chunks" / Area("Chunk" / Struct(
        "unk0" / Int32ul,
        "objectCount" / Int32ul,
    ), offset=this.offset, size=this.size),
)

# fourth table
CLASTable = Struct(
    "magic" / Magic(b"CLAS"),
    "pad0" / Const(b"\x00" * 4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._.CHNK.offset + foo._.CHNK._chunks_meta._ptrsize),
    "pad1" / Const(b"\x00" * 4),
    "size" / Rebuild(Int32ul, lambda foo: foo._classes_meta._ptrsize),
    "pad2" / Const(b"\x00" * 4),
    "classes" / Area("Class" / Struct(
        "name" / PascalString(Int32ul, "utf-8"),
    ), offset=this.offset, size=this.size),
)

# fifth table
PROPTable = Struct(
    "magic" / Magic(b"PROP"),
    "pad0" / Const(b"\x00" * 4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._.CLAS.offset + foo._.CLAS._classes_meta._ptrsize),
    "pad1" / Const(b"\x00" * 4),
    "size" / Rebuild(Int32ul, lambda foo: foo._properties_meta._ptrsize),
    "pad2" / Const(b"\x00" * 4),
    "properties" / Area("Property" / Struct(
        "name" / PascalString(Int32ul, "iso-8859-1"),
        "classIndex" / Int32ul,
    ), offset=this.offset, size=this.size),
)

# sixth table
STRGTable = Struct(
    "magic" / Magic(b"STRG"),
    "pad0" / Const(b"\x00" * 4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._.PROP.offset + foo._.PROP._properties_meta._ptrsize),
    "pad1" / Const(b"\x00" * 4),
    "size" / Rebuild(Int32ul, lambda foo: foo._strings_meta._ptrsize),
    "pad2" / Const(b"\x00" * 4),
    "strings" / Area("String" / Struct(
        "value" / PascalString(Int32ul, "iso-8859-1"),
    ), offset=this.offset, size=this.size),
)

# seventh table
TRANTable = Struct(
    "magic" / Magic(b"TRAN"),
    "pad0" / Const(b"\x00" * 4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._.STRG.offset + foo._.STRG._strings_meta._ptrsize),
    "pad1" / Const(b"\x00" * 4),
    "size" / Rebuild(Int32ul, lambda foo: foo._trans_meta._ptrsize),
    "pad2" / Const(b"\x00" * 4),
    "trans" / Area("Tran" / Struct(
        "name" / PascalString(Int32ul, "iso-8859-1"),
    ), offset=this.offset, size=this.size),
)

IMPR = Struct(
    "tranIndex" / Int32ul,
    "objectIndex" / Int32ul,
    "count" / Rebuild(Int32ul, lambda ctx: len(ctx.imprs)),
    "_impr_size" / Computed(lambda ctx: 12 + 4 * ctx.count + sum([x._impr_size for x in ctx.imprs]) if not ctx._parsing else 0),
    # sizes of following IMPR
    "improffsets" / Rebuild(Array(this.count, Int32ul), lambda ctx: [4*ctx.count +
                                                                     sum([x._impr_size for x in ctx.imprs[0:i]])
                                                                     for i in range(ctx.count) if ctx.count > 0
                                                                    ]),
    "imprs" / Array(this.count, LazyBound(lambda: IMPR)),
)
#IMPR = Struct(
#    "tranIndex" / Int32ul,
#    "objectIndex" / Int32ul,
#    "count" / Int32ul,
#    # sizes of following IMPR
#    "improffsets" / Array(this.count, Int32ul),
#    "imprs" / Array(this.count, LazyBound(lambda: IMPR)),
#)

# eight table
IMPRTable = Struct(
    "magic" / Magic(b"IMPR"),
    "pad0" / Const(b"\x00" * 4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._.TRAN.offset + foo._.TRAN._trans_meta._ptrsize),
    "pad1" / Const(b"\x00" * 4),
    "size" / Rebuild(Int32ul, lambda foo: foo._imprs_meta._ptrsize),
    "pad2" / Const(b"\x00" * 4),
    "imprs" / Area("Impr" / IMPR, offset=this.offset, size=this.size),
)

# nineth table
EXPRTable = Struct(
    "magic" / Magic(b"EXPR"),
    "pad0" / Const(b"\x00" * 4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._.IMPR.offset + foo._.IMPR._imprs_meta._ptrsize),
    "pad1" / Const(b"\x00" * 4),
    "size" / Rebuild(Int32ul, lambda foo: foo._exprs_meta._ptrsize),
    "pad2" / Const(b"\x00" * 4),
    "exprs" / Area("Expr" / IMPR, offset=this.offset, size=this.size),
)

TOC0Header = Struct(
    "magic" / Magic(b"TOC0"),
    "tableCount" / Const(9, Int32ul),
    "OBJE" / OBJETable,
    "TOPO" / TOPOTable,
    "CHNK" / CHNKTable,
    "CLAS" / CLASTable,
    "PROP" / PROPTable,
    "STRG" / STRGTable,
    "TRAN" / TRANTable,
    "IMPR" / IMPRTable,
    "EXPR" / EXPRTable,
)

NdfBin = Struct(
    "magic" / Magic(b"EUG0"),
    "magic2" / Magic(b"\x00\x00\x00\x00"),
    "magic3" / Magic(b"CNDF"),
    "compressed" / Enum(Int32ul, uncompressed=0x0, compressed=0x80),
    "toc0offset" / Int32ul,
    "unk0" / Int32ul,
    "headerSize" / Rebuild(Int32ul, this._unk4_meta._endoffset), # should be 40 always
    "unk2" / Int32ul,
    "size" / Int32ul,
    "unk4" / Int32ul,
    # this stuff now comes, because of the decompression, FIXME
    "uncompressedSize" / Int32ul,
    "toc0header" / Pointer(this.toc0offset, TOC0Header),
)


class NdfBinMain(CommonMain):
    def get_data(self, input):
        data = super().get_data(input)
        if not self.args.pack:
            return decompress_ndfbin(data)
        else:
            return data


if __name__ == "__main__":
    main = NdfBinMain(NdfBin, "NdfBin")
    main.main()
