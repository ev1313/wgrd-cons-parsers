#!/usr/bin/env python3
import sys
import pdb

from .ess import *
from .sformat import *

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=pathlib.Path, help="path to the ess file")
    parser.add_argument("-o", "--output", type=pathlib.Path, default="test.sformat",
                        help="path to the output sformat file")
    args = parser.parse_args()

    essfile = open(args.path, "rb")
    essdata = essfile.read()

    ess_header = Ess.parse(essdata)

    sformat = Container(
              unk0=0x6,
              isShort="true",
              channelCount=ess_header.channels,
              unk3=ess_header.channels*0x200,
              samplerate=ess_header.samplerate,
              frameCount=ess_header.frameCount,
              unk4=2,
              essLength=len(essdata),
              essUnk2=0,
              frameCount2=ess_header.frameCount,
              data=None)

    sformatdata = SFormat.build(sformat)

    sformatfile = open(args.output, "wb")
    sformatfile.write(sformatdata)
