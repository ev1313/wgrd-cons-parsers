#!/usr/bin/env python3

import pdb

import os
import sys
import pathlib
import argparse

from cons_utils import *
from cons_xml import *

from construct import *

Ess = Struct(
    # FIXME: is this really a version number or maybe something else?
    "version" / Const(b"\x01\x00\x02\x02"),
    "isShort" / Enum(Int8ul, false=0, true=1),
    "channels" / Int8ul,
    "samplerate" / Int16ul,
    "frameCount" / Int32ub,
    "pad" / Const(b"\x00"*4),
    "samplecount2" / Int32ub,
    "sampleoffsets" / RepeatUntil(lambda obj,lst,ctx: obj == 0, Int32ub),
    "padding" / Const(b"\x00"*16),
    "framedata" / GreedyBytes,
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
            sys.stderr.write("parsing ess...\n")
            ess = Ess.parse(data)
            sys.stderr.write("generating xml...\n")
            xml = Ess.toET(ess, name="Ess", is_root=True)
            sys.stderr.write("indenting xml...\n")
            ET.indent(xml, space="  ", level=0)
            str = ET.tostring(xml).decode("utf-8")
            sys.stderr.write("writing xml...\n")
            f = open(os.path.join(args.output, f"{os.path.basename(input)}.xml"), "wb")
            f.write(str.encode("utf-8"))
            f.close()
        else:
            assert(str(input).endswith(".ess.xml"))
            xml = ET.fromstring(data.decode("utf-8"))
            sys.stderr.write("rebuilding from xml...\n")
            ctx, size = Ess.fromET(context={}, parent=xml, name="Dic", is_root=True)
            sys.stderr.write("building ess...\n")
            rebuilt_data = Ess.build(ctx)
            sys.stderr.write("writing ess...\n")
            f = open(os.path.join(args.output, f"{os.path.basename(str(input)[:-4])}"), "wb")
            f.write(rebuilt_data)
            f.close()
