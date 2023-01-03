import pdb

import os
import sys
import argparse
import pathlib
from io import BytesIO
import sys

from cons_xml import *


def commonMain(structure, structureName):
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pack", action="store_true")
    parser.add_argument("inputs", type=pathlib.Path, nargs='+', help="path to the input directory (pack) or file (unpack)")
    parser.add_argument("-o", "--output", type=pathlib.Path, default="./out/", help="path to the output directory (unpack) / file (pack)")
    args = parser.parse_args()

    extName = ".%s.xml" % structureName.lower()

    for input in args.inputs:
        f = open(input, "rb")
        data = f.read()
        f.close()

        if not args.pack:
            sys.stderr.write("parsing %s...\n" % structureName)
            object = structure.parse(data)
            sys.stderr.write("generating xml...\n")
            xml = structure.toET(object, name=structureName, is_root=True)
            sys.stderr.write("indenting xml...\n")
            ET.indent(xml, space="  ", level=0)
            s = ET.tostring(xml).decode("utf-8")
            sys.stderr.write("writing xml...\n")
            f = open(os.path.join(args.output, f"{os.path.basename(input)}.xml"), "wb")
            f.write(s.encode("utf-8"))
            f.close()
        else:
            assert(str(input).endswith(extName))
            xml = ET.fromstring(data.decode("utf-8"))
            sys.stderr.write("rebuilding from xml...\n")
            ctx, size = structure.fromET(context={}, parent=xml, name=structureName, is_root=True)
            sys.stderr.write("building %s...\n" % structureName)
            rebuilt_data = structure.build(ctx)
            sys.stderr.write("writing %s...\n" % structureName)
            f = open(os.path.join(args.output, f"{os.path.basename(str(input)[:-4])}"), "wb")
            f.write(rebuilt_data)
            f.close()
