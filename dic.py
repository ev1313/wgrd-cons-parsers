#!/usr/bin/env python3

import pdb

import os
import sys
import argparse
import pathlib
from io import BytesIO

from cons_utils import *
from cons_xml import *

Dic = Struct(
    "magic" / Const(b"TRAD"),
    "count" / Rebuild(Int32ul, len_(this.entries)),
    "entries" / Array(this.count, "Entry" / Struct(
        "hash" / Int64ul,
        "offset" / Rebuild(Int32ul, lambda ctx: ctx._._endoffset_entries + sum([x["_ptrsize_string"] for x in ctx._.entries[0:ctx._index]])),
        "length" / Rebuild(Int32ul, lambda ctx: len(ctx.string)),
        "string" / Pointer(this.offset, PaddedString(this.length*2, "utf-16-le")),
    )),
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
            sys.stderr.write("parsing dic...\n")
            dic = Dic.parse(data)
            sys.stderr.write("generating xml...\n")
            xml = Dic.toET(dic, name="Dic", is_root=True)
            sys.stderr.write("indenting xml...\n")
            ET.indent(xml, space="  ", level=0)
            str = ET.tostring(xml).decode("utf-8")
            sys.stderr.write("writing xml...\n")
            f = open(os.path.join(args.output, f"{os.path.basename(input)}.xml"), "wb")
            f.write(str.encode("utf-8"))
            f.close()
        else:
            assert(str(input).endswith(".dic.xml"))
            xml = ET.fromstring(data.decode("utf-8"))
            sys.stderr.write("rebuilding from xml...\n")
            xml_rebuild, size, _ = Dic.fromET(xml, "Dic", is_root=True)
            sys.stderr.write("building dic...\n")
            rebuilt_data = Dic.build(xml_rebuild)
            sys.stderr.write("writing dic...\n")
            f = open(os.path.join(args.output, f"{os.path.basename(str(input)[:-4])}"), "wb")
            f.write(rebuilt_data)
            f.close()
