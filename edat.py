#!/usr/bin/env python3

import pdb

import os
import sys
import argparse
import pathlib
from io import BytesIO

from cons_utils import *
from cons_xml import *


EDat = Struct(
    "magic" / Magic(b"edat"),
    "unk0" / Const(2, Int32ul), # number of tables maybe?
    "pad0" / Padding(17),
    #"files" / Dictionary(EDatFileHeader),
    #"data" /
    "pad1" / Padding(4),
    "sectorSize" / Int32ul,
    "checksum" / Bytes(16),
    "pad2" / Padding(972),
)

