#!/usr/bin/env python3

import pdb

import os
import sys
import argparse
import pathlib
from io import BytesIO

from cons_utils import *
from cons_xml import *

from common import *
from dictionary import *

def Header(subcon):
    H = Struct(
        "offset" / Int32ul,
        "size" / Int32ul,
        "data" / Pointer(this.offset, subcon),
    )
    return H

def HeaderWithCount(subcon):
    HWC = Struct(
        "offset" / Int32ul,
        "size" / Int32ul,
        "count" / Int32ul,
        "data" / Pointer(this.offset, subcon)
    )
    return HWC

FileItem = Struct(
    "minX" / Float32l,
    "minY" / Float32l,
    "minZ" / Float32l,
    "maxX" / Float32l,
    "maxY" / Float32l,
    "maxZ" / Float32l,
    "flags" / Int32ul,
    Check(lambda ctx: ctx.flags in [0x0, 0x1]),
    "meshIndex" / Int16ul,
    "nodesIndex" / Int16ul,
)

Spk = Struct(
    "typeMagic" / Const(b"MESH"),
    "platformMagic" / Const(b"PCPC"),
    "version" / Const(7, Int32ul),
    "fileSize" / Int32ul,
    "checksum" / Bytes(16),
    "block1" / Header(Bytes(this.size)),
    "block2" / HeaderWithCount(Bytes(this.size)),
    "files" / HeaderWithCount(Dictionary(FileItem, this.offset, this.size)),
    "vertexFormats" / HeaderWithCount(Bytes(this.size)),
    "materials" / HeaderWithCount(Bytes(this.size)),
    "unknown0" / HeaderWithCount(Bytes(this.size)),
    "unknown1" / HeaderWithCount(Bytes(this.size)),
    "meshes" / HeaderWithCount(Bytes(this.size)),
    "drawCalls" / HeaderWithCount(Bytes(this.size)),
    "ibufTable" / HeaderWithCount(Bytes(this.size)),
    "ibufData" / Header(Bytes(this.size)),
    "vbufTable" / HeaderWithCount(Bytes(this.size)),
    "vbufData" / Header(Bytes(this.size)),
    "nodesTable" / HeaderWithCount(Bytes(this.size)),
    "nodesData" / Header(Bytes(this.size)),
    "unknown10" / HeaderWithCount(Bytes(this.size)),
    "unknown10indices" / HeaderWithCount(Bytes(this.size)),
)

if __name__ == "__main__":
    commonMain(Spk, "Spk")
