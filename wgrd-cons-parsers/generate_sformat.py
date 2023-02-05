#!/usr/bin/env python3
import sys
import pdb

from .ess import *
from .sformat import *

if __name__ == "__main__":
    essfile = open(sys.argv[1], "rb")
    essdata = essfile.read()

    ess_header = Ess.parse(essdata)

    sformat = Container(
              unk0=0x6,
              isShort="true",
              channelCount=ess_header.channels,
              unk3=ess_header.channels*0x200,
              samplerate=ess_header.samplerate,
              frameCount=ess_header.frameCount,
              length=2,
              essLength=len(essdata),
              essUnk2=0,
              frameCount2=ess_header.frameCount,
              data=None)

    sformatdata = SFormat.build(sformat)

    sformatfile = open(sys.argv[2], "wb")
    sformatfile.write(sformatdata)
