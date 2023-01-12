import pdb

import os
import sys
import argparse
import pathlib
from io import BytesIO
import sys

from cons_xml import *


class CommonMain:
    def __init__(self, subcon, sc_name):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-p", "--pack", action="store_true")
        self.parser.add_argument("inputs", type=pathlib.Path, nargs='+',
                                 help="path to the input directory (pack) or file (unpack)")
        self.parser.add_argument("-o", "--output", type=pathlib.Path, default="./out/",
                                 help="path to the output directory (unpack) / file (pack)")

        self.subcon = subcon
        self.sc_name = sc_name
        self.extName = ".%s.xml" % sc_name.lower()

    def add_extra_args(self, input, ctx={}):
        extra_args = ctx
        if self.args.pack:
            extra_args["_cons_xml_input_directory"] = os.path.dirname(input)
        else:
            extra_args["_cons_xml_output_directory"] = self.args.output

        return extra_args

    def get_data(self, input):
        f = open(input, "rb")
        data = f.read()
        f.close()
        return data

    def parse(self):
        self.args = self.parser.parse_args()

    def main(self):
        self.parse()
        for input in self.args.inputs:
            data = self.get_data(input)

            if not self.args.pack:
                sys.stderr.write("parsing %s...\n" % self.sc_name)
                ctx = self.add_extra_args(input)
                ctx = self.subcon.parse(data, **ctx)
                sys.stderr.write("generating xml...\n")
                xml = self.subcon.toET(ctx, name=self.sc_name, is_root=True)
                sys.stderr.write("indenting xml...\n")
                ET.indent(xml, space="  ", level=0)
                s = ET.tostring(xml).decode("utf-8")
                sys.stderr.write("writing xml...\n")
                f = open(os.path.join(self.args.output, f"{os.path.basename(input)}.xml"), "wb")
                f.write(s.encode("utf-8"))
                f.close()
            else:
                xml = ET.fromstring(data.decode("utf-8"))
                sys.stderr.write("rebuilding from xml...\n")
                ctx = self.add_extra_args(input)
                ctx, size = self.subcon.fromET(context=ctx, parent=xml, name=self.sc_name, is_root=True)
                sys.stderr.write("building %s...\n" % self.sc_name)
                rebuilt_data = self.subcon.build(ctx)
                sys.stderr.write("writing %s...\n" % self.sc_name)
                f = open(os.path.join(self.args.output, f"{os.path.basename(str(input)[:-4])}"), "wb")
                f.write(rebuilt_data)
                f.close()
