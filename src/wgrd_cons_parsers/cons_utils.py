import os
from io import BytesIO
import xml.etree.ElementTree as ET

from conshex import *
from conshex.lib import *
from conshex.helpers import *
from conshex.string import *

import zlib
from functools import partial
import itertools


def compress_zlib(data, level=9, wbits=15, depth=0):
    print("  " * depth + "compressing zlib data")
    d = data
    io = BytesIO(d)
    data = BytesIO()
    z = zlib.compressobj(level=level, wbits=wbits)
    for block in iter(partial(io.read, 8192), b''):
        data.write(z.compress(block))
    data.write(z.flush(zlib.Z_FULL_FLUSH))
    return bytes(data.getbuffer())


def decompress_zlib(data, wbits=0, depth=0):
    d = data
    fi = BytesIO(d)

    g = b''
    z = zlib.decompressobj(wbits)
    while True:
        buf = z.unconsumed_tail
        if buf == b"":
            buf = fi.read(8192)
            if buf == b"":
                break
        got = z.decompress(buf)
        if got == b"":
            break
        g += got
        # print(g)
    return g


class ZlibCompressed(Adapter):

    def __init__(self, subcon):
        super().__init__(subcon)

    def _decode(self, obj, context, path):
        decompressed_data = decompress_zlib(obj)
        self.decompressed_size = len(decompressed_data)
        return decompressed_data

    def _encode(self, obj, context, path):
        self.decompressed_size = len(obj)
        return compress_zlib(obj)

    def _toET(self, parent, name, context, path):
        Bytes._toET(self, parent, name, context, path)

    def _fromET(self, parent, name, context, path, is_root=False):
        return Bytes._fromET(self, parent, name, context, path, is_root=is_root)


class File(Adapter):
    """
    Adapter for reading/writing files of the values in the subcon.

    If the context contains a key "_cons_xml_output_directory", the file will be written there when decoding.

    If the context contains a key "_cons_xml_input_directory", the file will be read from there when encoding.

    The filepath is written in the dictionary / XML afterwards.
    """
    def __init__(self, subcon, path):
        super().__init__(subcon)
        self._path = path

    def _decode(self, obj, context, path):
        p = evaluate(self._path, context)
        if "_root" in context.keys():
            outpath = context["_root"].get("_cons_xml_output_directory", "out")
        else:
            outpath = context.get("_cons_xml_output_directory", "out")
        joined_path = os.path.join(outpath, p)
        os.makedirs(os.path.dirname(joined_path), exist_ok=True)
        f = open(joined_path, "wb")
        assert(isinstance(obj, bytes))
        f.write(obj)
        f.close()
        return p

    def _encode(self, obj, context, path):
        if isinstance(obj, bytes):
            return obj

        if "_root" in context.keys():
            inpath = context["_root"].get("_cons_xml_input_directory", "out")
        else:
            inpath = context.get("_cons_xml_input_directory", "out")

        joined_path = os.path.join(inpath, obj)
        f = open(joined_path, "rb")
        data = f.read()
        f.close()
        return data

    def _toET(self, parent, name, context, path):
        return StringEncoded._toET(self, parent, name, context, path)

    def _fromET(self, parent, name, context, path, is_root=False):
        if "_root" in context.keys():
            inpath = context["_root"].get("_cons_xml_input_directory", "out")
        else:
            inpath = context.get("_cons_xml_input_directory", "out")

        self.encoding = "utf-8"
        ctx = StringEncoded._fromET(self, parent, name, context, path, is_root=is_root)
        path = ctx[name]
        p = os.path.join(inpath, path)
        f = open(p, "rb")
        ctx[name] = f.read()
        f.close()
        return ctx

