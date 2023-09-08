import pdb

import os
import sys
import argparse
import pathlib
import sys

from dingsda import *
import xml.etree.ElementTree as ET

import gc

class CommonMain:
    def __init__(self, subcon: Construct, sc_name: str):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-p", "--pack", action="store_true")
        self.parser.add_argument("inputs", type=pathlib.Path, nargs='+',
                                 help="paths to the input files")
        self.parser.add_argument("-o", "--output", type=pathlib.Path, default="./out/",
                                 help="path to the output directory (unpack) / file (pack)")

        self.subcon = subcon
        self.sc_name = sc_name
        self.extName = ".%s.xml" % sc_name.lower()

    def add_extra_args(self, input_path: pathlib.Path, ctx=None) -> dict:
        if ctx is None:
            ctx = {}
        extra_args = ctx
        extra_args["_cons_xml_input_directory"] = os.path.dirname(input_path)
        extra_args["_cons_xml_output_directory"] = self.args.output

        return extra_args

    def get_data(self, input_path: pathlib.Path) -> bytes:
        f = open(input_path, "rb")
        data = f.read()
        f.close()
        return data

    def parse(self, args: argparse.Namespace = None):
        if args:
            self.args = self.parser.parse_args(args)
        else:
            self.args = self.parser.parse_args()

    def unpack(self, input_path: pathlib.Path, data: bytes):
        sys.stderr.write(f"parsing {self.sc_name} {input_path}\n")
        ctx = self.add_extra_args(input_path)
        ctx = self.subcon.parse(data, **ctx)
        ctx = ctx | self.add_extra_args(input_path)
        sys.stderr.write(f"generating xml...\n")
        xml = self.subcon.toET(ctx, name=self.sc_name, is_root=True)
        sys.stderr.write("indenting xml...\n")
        ET.indent(xml, space="  ", level=0)
        s = ET.tostring(xml).decode("utf-8")
        sys.stderr.write(f"writing xml {os.path.basename(input_path)}.xml\n")
        os.makedirs(self.args.output, exist_ok=True)
        f = open(os.path.join(self.args.output, f"{os.path.basename(input_path)}.xml"), "wb")
        f.write(s.encode("utf-8"))
        f.close()
    
    def pack(self, input_path: pathlib.Path, data: bytes):
        xml = ET.fromstring(data.decode("utf-8"))
        sys.stderr.write("rebuilding from xml...\n")
        ctx = self.add_extra_args(input_path)
        ctx = self.subcon.fromET(xml)
        preprocessed_ctx, _ = self.subcon.preprocess(ctx)
        del xml
        del ctx
        gc.collect()
        sys.stderr.write("building %s...\n" % self.sc_name)
        rebuilt_data = self.subcon.build(preprocessed_ctx)
        sys.stderr.write("writing %s...\n" % self.sc_name)
        f = open(os.path.join(self.args.output, f"{os.path.basename(str(input_path)[:-4])}"), "wb")
        f.write(rebuilt_data)
        f.close()

    def main(self, args: argparse.Namespace = None):
        self.parse(args)
        for input_path in self.args.inputs:
            data = self.get_data(input_path)
            if not self.args.pack:
                self.unpack(input_path, data)
            else:
                self.pack(input_path, data)