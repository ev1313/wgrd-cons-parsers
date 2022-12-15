#!/usr/bin/env python3

import pdb

import os
import sys
import argparse
import pathlib
from io import BytesIO

from cons_utils import *
from cons_xml import *

from compress_ndfbin import compress_ndfbin
from decompress_ndfbin import decompress_ndfbin

NDFType = Struct(
    "typeId" / Rebuild(Int32ul, this._switchid_data),
    "data" / Switch(this.typeId, {
        0x00000000: "Boolean" / Struct("value" / Enum(Int8ul, false=0, true=1)),
        0x00000001: "Int8" / Struct("value" / Int8ul),
        0x00000002: "Int32" / Struct("value" / Int32sl),
        0x00000003: "UInt32" / Struct("value" / Int32ul),
        0x00000005: "Float32" / Struct("value" / Float32l),
        0x00000006: "Float64" / Struct("value" / Float64l),
        0x00000007: "StringReference" / Struct("stringIndex" / Int32ul),
        0x00000008: "WideString" / PascalString(Int32ul, "utf-16"),
        0x00000009: "Reference" / LazyBound(lambda: NDFType),
        0x0000000B: "F32_vec3" / Struct("x" / Float32l, "y" / Float32l, "z" / Float32l),
        0x0000000C: "F32_vec4" / Struct("x" / Float32l, "y" / Float32l, "z" / Float32l, "w" / Float32l),
        0x0000000D: "Color" / Struct("r" / Int8ul, "g" / Int8ul, "b" / Int8ul, "a" / Int8ul),
        0x0000000E: "S32_vec3" / Struct("x" / Int32sl, "y" / Int32sl, "z" / Int32sl),
        0x0000000F: "Matrix" / Array(16, Float32l),
        0x00000011: "List" / Struct("count" / Rebuild(Int32ul, len_(this.listitem)),
                                    "listitem" / Array(this.count, LazyBound(lambda: NDFType)),
                                    ),
        0x00000012: "Map" / Struct(
            "count" / Rebuild(Int32ul, len_(this.mapitem)),
            "mapitem" / Struct(
                "key" / LazyBound(lambda: NDFType),
                "value" / LazyBound(lambda: NDFType),
                )[this.count]),
        0x00000013: "Long" / Int64ul,
        0x00000014: "Blob" / Struct(
            "_size" / Int32ul,
            "data" / Bytes(this._size),
            ),
        0x00000018: "S16" / Struct("value" / Int16sl),
        0x00000019: "U16" / Struct("value" / Int16ul),
        0x0000001A: "GUID" / Struct("data" / Bytes(16)),
        0x0000001C: "PathReference" / Struct("stringIndex" / Int32ul),
        0x0000001D: "LocalisationHash" / Struct("data" / Bytes(8)),
        0x00000022: "Pair" / Struct(
            "first" / LazyBound(lambda: NDFType),
            "second" / LazyBound(lambda: NDFType),
            ),
        0x0000001F: "S32_vec2" / Struct("x" / Int32sl, "y" / Int32sl),
        0x00000021: "F32_vec2" / Struct("x" / Float32l, "y" / Float32l),
        0x00000025: "Hash" / Bytes(16),
        #FIXME: The following are probably part of 0x00000009 (Reference)
        0xAAAAAAAA: "TranReference" / Int32ul,
        0xBBBBBBBB: "ObjectReference" / Struct(
            "objectIndex" / Int32ul,
            "classIndex" / Int32ul,
            ),
    }, default=Error),
    )

NDFProperty = Struct(
    "propertyIndex" / Rebuild(Int32ul, lambda ctx: ctx._index),
    "value" / If(lambda ctx: ctx.propertyIndex != 0xABABABAB, NDFType),
    )

NDFObject = Struct(
    "classIndex" / Rebuild(Int32ul, lambda ctx: ctx._index),
    "properties" / RepeatUntil(lambda obj, lst, ctx: obj.propertyIndex == 0xABABABAB, NDFProperty),
    )

# generic table
TOC0Table = Struct(
    "magic" / Bytes(4),
    "pad0" / Const(b"\x00"*4),
    "offset" / Int32ul,
    "pad1" / Const(b"\x00"*4),
    "size" / Int32ul,
    "pad2" / Const(b"\x00"*4),
    )

# first table
OBJETable = Struct(
    "magic" / Magic(b"OBJE"),
    "pad0" / Const(b"\x00"*4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._._.headerSize),
    "pad1" / Const(b"\x00"*4),
    "size" / Rebuild(Int32ul, lambda foo: foo._ptrsize_objects),
    "pad2" / Const(b"\x00"*4),
    "objects" / readArea(NDFObject),
)

# second table
TOPOTable = Struct(
    "magic" / Magic(b"TOPO"),
    "pad0" / Const(b"\x00"*4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._.OBJE.offset + foo._.OBJE._ptrsize_objects),
    "pad1" / Const(b"\x00"*4),
    "size" / Rebuild(Int32ul, lambda foo: foo._ptrsize_topobjects),
    "pad2" / Const(b"\x00"*4),
    "topobjects" / readArea("TopObject" / Struct(
        "objectIndex" / Int32ul,
        )),
)

# third table
CHNKTable = Struct(
    "magic" / Magic(b"CHNK"),
    "pad0" / Const(b"\x00"*4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._.TOPO.offset + foo._.TOPO._ptrsize_topobjects),
    "pad1" / Const(b"\x00"*4),
    "size" / Rebuild(Int32ul, lambda foo: foo._ptrsize_chunks),
    "pad2" / Const(b"\x00"*4),
    # FIXME: check if unk0 is topOfObjectIndex
    "chunks" / readArea("Chunk" / Struct(
        "unk0" / Int32ul,
        "objectCount" / Int32ul,
        )),
)

# fourth table
CLASTable = Struct(
    "magic" / Magic(b"CLAS"),
    "pad0" / Const(b"\x00" * 4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._.CHNK.offset + foo._.CHNK._ptrsize_chunks),
    "pad1" / Const(b"\x00" * 4),
    "size" / Rebuild(Int32ul, lambda foo: foo._ptrsize_classes),
    "pad2" / Const(b"\x00" * 4),
    "classes" / readArea("Class" / Struct(
        "_tell_start" / Tell,
        "name" / PascalString(Int32ul, "utf-8"),
        "_tell_end" / Tell,
        "_size" / Computed(this._tell_end - this._tell_start),
        )),
)

# fifth table
PROPTable = Struct(
    "magic" / Magic(b"PROP"),
    "pad0" / Const(b"\x00" * 4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._.CLAS.offset + foo._.CLAS._ptrsize_classes),
    "pad1" / Const(b"\x00" * 4),
    "size" / Rebuild(Int32ul, lambda foo: foo._ptrsize_properties),
    "pad2" / Const(b"\x00" * 4),
    "properties" / readArea("Property" / Struct(
        "name" / PascalString(Int32ul, "iso-8859-1"),
        "classIndex" / Int32ul,
    )),
)

# sixth table
STRGTable = Struct(
    "magic" / Magic(b"STRG"),
    "pad0" / Const(b"\x00"*4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._.PROP.offset + foo._.PROP._ptrsize_properties),
    "pad1" / Const(b"\x00"*4),
    "size" / Rebuild(Int32ul, lambda foo: foo._ptrsize_strings),
    "pad2" / Const(b"\x00"*4),
    "strings" / readArea("String" / Struct(
        "value" / PascalString(Int32ul, "iso-8859-1"),
        )),
)

# seventh table
TRANTable = Struct(
    "magic" / Magic(b"TRAN"),
    "pad0" / Const(b"\x00"*4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._.STRG.offset + foo._.STRG._ptrsize_strings),
    "pad1" / Const(b"\x00"*4),
    "size" / Rebuild(Int32ul, lambda foo: foo._ptrsize_trans),
    "pad2" / Const(b"\x00"*4),
    "trans" / readArea("Tran" / Struct(
        "name" / PascalString(Int32ul, "iso-8859-1"),
        )),
)

IMPR = Struct(
    "tranIndex" / Int32ul,
    "objectIndex" / Int32ul,
    "count" / Rebuild(Int32ul, len_(this.imprsizes)),
    # sizes of following IMPR
    "imprsizes" / Rebuild(Array(this.count, Int32ul), lambda ctx: [x._size for x in ctx.imprs]),
    "imprs" / Array(this.count, LazyBound(lambda: IMPR))
    )

# eight table
IMPRTable = Struct(
    "magic" / Magic(b"IMPR"),
    "pad0" / Const(b"\x00"*4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._.TRAN.offset + foo._.TRAN._ptrsize_trans),
    "pad1" / Const(b"\x00"*4),
    "size" / Rebuild(Int32ul, lambda foo: foo._ptrsize_imprs),
    "pad2" / Const(b"\x00"*4),
    "imprs" / readArea("Impr" / IMPR),
)

# nineth table
EXPRTable = Struct(
    "magic" / Magic(b"EXPR"),
    "pad0" / Const(b"\x00"*4),
    "offset" / Rebuild(Int32ul, lambda foo: foo._.IMPR.offset + foo._.IMPR._ptrsize_imprs),
    "pad1" / Const(b"\x00"*4),
    "size" / Rebuild(Int32ul, lambda foo: foo._ptrsize_exprs),
    "pad2" / Const(b"\x00"*4),
    "exprs" / readArea("Expr" / IMPR),
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
    "headerSize" / Rebuild(Int32ul, this._size),
    "unk2" / Int32ul,
    "size" / Int32ul,
    "unk4" / Int32ul,
    # this stuff now comes, because of the decompression, FIXME
    "uncompressedSize" / Int32ul,
    "toc0header" / Pointer(this.toc0offset, TOC0Header),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pack", action="store_true")
    parser.add_argument("inputs", type=pathlib.Path, nargs='+', help="path to the input directory (pack) or file (unpack)")
    parser.add_argument("-o", "--output", type=pathlib.Path, default="./out/", help="path to the output directory (unpack) / file (pack)")
    args = parser.parse_args()

    for input in args.inputs:
        f = open(input, "rb")
        data = f.read()
        f.close()

        if not args.pack:
            data = decompress_ndfbin(data)
            sys.stderr.write("parsing NdfBin...\n")
            ndfbin = NdfBin.parse(data)
            sys.stderr.write("generating xml...\n")
            xml = NdfBin.toET(ndfbin, name="NdfBin", is_root=True)
            sys.stderr.write("indenting xml...\n")
            ET.indent(xml, space="  ", level=0)
            str = ET.tostring(xml).decode("utf-8")
            sys.stderr.write("writing xml...\n")
            f = open(os.path.join(args.output, f"{os.path.basename(input)}.xml"), "wb")
            f.write(str.encode("utf-8"))
            f.close()
        else:
            assert(str(input).endswith(".ndfbin.xml"))
            xml = ET.fromstring(data.decode("utf-8"))
            sys.stderr.write("rebuilding from xml...\n")
            xml_rebuild, size, _ = NdfBin.fromET(xml, "NdfBin", is_root=True)
            sys.stderr.write("building ndfbin...\n")
            rebuilt_data = NdfBin.build(xml_rebuild)
            sys.stderr.write("writing ndfbin...\n")
            f = open(os.path.join(args.output, f"{os.path.basename(str(input)[:-4])}"), "wb")
            rebuilt_data = compress_ndfbin(rebuilt_data)
            f.write(rebuilt_data)
            f.close()
