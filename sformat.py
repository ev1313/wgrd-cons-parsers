#!/usr/bin/env python3

import sys
import pdb

import sys
import os
import pathlib
import argparse

from cons_utils import *
from cons_xml import *

SFormat = Struct(
    "unk0" / Const(0x06, Int8ul),
    "unk1" / Const(0x01, Int8ul),
    "isShort" / Enum(Int8ul, false=0, true=1),
    "channelCount" / Int8ul,
    "unk3" / Int16ul, # channelCount * 0x200
    "samplerate" / Int16ub,
    "frameCount" / Int32ul,
    "length" / Int32ul,
    "sformatLength" / Int32ul,
    "sformatUnk2" / Int32ul,
    "frameCount2" / Int32ul,
    "data" / If(lambda ctx: ctx.isShort == "false",
               Struct(
                   "unkCount" / Int32ul,
                   "unkX" / Int16ul,
                   "unkY" / Const(10, Int8ul),
                   "unkZ" / Const(5, Int8ul),
                   "data" / Array(this.unkCount, "item" / Struct("data" / Array(5, Int8ul))),
                   )
               ),
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
            sys.stderr.write("parsing sformat...\n")
            sformat = SFormat.parse(data)
            sys.stderr.write("generating xml...\n")
            xml = SFormat.toET(sformat, name="SFormat", is_root=True)
            sys.stderr.write("indenting xml...\n")
            ET.indent(xml, space="  ", level=0)
            str = ET.tostring(xml).decode("utf-8")
            sys.stderr.write("writing xml...\n")
            f = open(os.path.join(args.output, f"{os.path.basename(input)}.xml"), "wb")
            f.write(str.encode("utf-8"))
            f.close()
        else:
            assert(str(input).endswith(".sformat.xml"))
            xml = ET.fromstring(data.decode("utf-8"))
            sys.stderr.write("rebuilding from xml...\n")
            xml_rebuild, size, _ = SFormat.fromET(xml, "SFormat", is_root=True)
            sys.stderr.write("building sformat...\n")
            rebuilt_data = SFormat.build(xml_rebuild)
            sys.stderr.write("writing sformat...\n")
            f = open(os.path.join(args.output, f"{os.path.basename(str(input)[:-4])}"), "wb")
            f.write(rebuilt_data)
            f.close()
