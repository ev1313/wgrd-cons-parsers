#!/usr/bin/env python3

import pdb

import os
import sys
import argparse
import pathlib
from io import BytesIO

from cons_utils import *
from cons_xml import *
from dictionary import *

EDatFileHeader = Struct(
    "offset" / Int32ul,
    "pad0" / Padding(4),
    "size" / Int32ul,
    "pad" / Padding(4),
    "checksum" / Bytes(16), # md5 checksum of the file itself
)

EDat = Struct(
    "magic" / Magic(b"edat"),
    "unk0" / Const(2, Int32ul), # number of tables maybe?
    "pad0" / Padding(17),
    "offset_files" / Rebuild(Int32ul, this._files_dictionary_offset),
    "size_files" / Rebuild(Int32ul, this._files_dictionary_size),
    "offset_data" / Rebuild(Int32ul, this._files_data_offset),
    "size_data" / Rebuild(Int32ul, this._files_data_size),
    "pad1" / Padding(4),
    "sectorSize" / Int32ul,
    "checksum" / Rebuild(Bytes(16), this._files_dictionary_checksum), # md5 checksum of the whole files section
    "pad2" / Padding(972),
    "files" / FileDictionary(EDatFileHeader, this.offset_files, this.size_files, this.offset_data, this.size_data, this.sectorSize),
    #"data" /
)

class EdatMain(CommonMain):
    def parse(self):
        self.parser.add_argument("-c", "--compat", action="store_true",
                            help="compatibility mode for enokhas ModdingSuite, which doesn't align the files correctly")
        self.parser.add_argument("--disable-checks", action="store_true",
                            help="compatibility mode for some WARNO files, which seem to have broken checksums")
        super().parse()

    def add_extra_args(self, input, ctx={}):
        ctx = {"_cons_xml_filesdictionary_alignment": not args.compat,
                   "_cons_xml_filesdictionary_disable_checks": args.disable_checks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pack", action="store_true")
    parser.add_argument("inputs", type=pathlib.Path, nargs='+', help="path to the input directory (pack) or file (unpack)")
    parser.add_argument("-o", "--output", type=pathlib.Path, default="./out/", help="path to the output directory (unpack) / file (pack)")
    parser.add_argument("-c", "--compat", action="store_true", help="compatibility mode for enokhas ModdingSuite, which doesn't align the files correctly")
    parser.add_argument("--disable-checks", action="store_true", help="compatibility mode for some WARNO files, which seem to have broken checksums")
    args = parser.parse_args()

    for input in args.inputs:
        f = open(input, "rb")
        data = f.read()
        f.close()

        if not args.pack:
            sys.stderr.write("parsing edat...\n")
            context = {"_cons_xml_filesdictionary_alignment": not args.compat,
                       "_cons_xml_filesdictionary_disable_checks": args.disable_checks}
            ctx = EDat.parse(data, **context)
            ctx["_cons_xml_output_directory"] = args.output
            sys.stderr.write("generating xml...\n")
            xml = EDat.toET(context=ctx, name="EDat", parent=None, is_root=True)
            sys.stderr.write("indenting xml...\n")
            ET.indent(xml, space="  ", level=0)
            str = ET.tostring(xml).decode("utf-8")
            sys.stderr.write("writing xml...\n")
            f = open(os.path.join(args.output, f"{os.path.basename(input)}.xml"), "wb")
            f.write(str.encode("utf-8"))
            print(xml)
        else:
            assert(len(os.path.basename(str(input))) >= 5)
            xml = ET.fromstring(data.decode("utf-8"))
            sys.stderr.write("rebuilding from xml...\n")
            ctx = {"_cons_xml_input_directory": os.path.dirname(input)}
            ctx, size = EDat.fromET(context=ctx, parent=xml, name="EDat", is_root=True)
            sys.stderr.write("building edat...\n")
            rebuilt_data = EDat.build(ctx)
            sys.stderr.write("writing edat...\n")
            f = open(os.path.join(args.output, f"{os.path.basename(str(input)[:-4])}"), "wb")
            f.write(rebuilt_data)
            f.close()