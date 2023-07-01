import os
from io import BytesIO
import xml.etree.ElementTree as ET

from dingsda import *
from dingsda.lib import *

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

    def toET(self, context, name=None, parent=None):
        return Bytes_toET(self, context, name, parent)

    def fromET(self, context, parent, name, offset=0, is_root=False):
        return Bytes_fromET(self, context=context, parent=parent, name=name, offset=offset, is_root=is_root)


class File(Adapter):
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

    def toET(self, context, name=None, parent=None, is_root=False):
        return StringEncoded_toET(self, context, name, parent, is_root=is_root)

    def fromET(self, context, parent, name, offset=0, is_root=False):
        if "_root" in context.keys():
            inpath = context["_root"].get("_cons_xml_input_directory", "out")
        else:
            inpath = context.get("_cons_xml_input_directory", "out")

        self.encoding = "utf-8"
        ctx, size = StringEncoded_fromET(self, context=context, parent=parent, name=name, offset=offset, is_root=is_root)
        path = ctx[name]
        p = os.path.join(inpath, path)
        f = open(p, "rb")
        ctx[name] = f.read()
        f.close()
        return ctx, os.stat(p).st_size



#class RepeatUntilSize(Subconstruct):
#    def __init__(self, predicate, subcon, discard=False):
#        super().__init__(subcon)
#        self.predicate = predicate
#        self.discard = discard
#
#    def _parse(self, stream, context, path):
#        predicate = self.predicate
#        discard = self.discard
#        if not callable(predicate):
#            predicate = lambda _1, _2, _3: predicate
#        obj = ListContainer()
#        for i in itertools.count():
#            context._index = i
#            e = self.subcon._parsereport(stream, context, path)
#            if not discard:
#                obj.append(e)
#            if predicate(e, obj, context):
#                return obj
#
#    def _build(self, obj, stream, context, path):
#        discard = self.discard
#        partiallist = ListContainer()
#        retlist = ListContainer()
#        for i, e in enumerate(obj):
#            context._index = i
#            buildret = self.subcon._build(e, stream, context, path)
#            if not discard:
#                retlist.append(buildret)
#                partiallist.append(buildret)
#        return retlist
#
#    def _sizeof(self, context, path):
#        raise SizeofError("cannot calculate size, amount depends on actual data", path=path)
#
#
#RepeatUntilSize.toET = GenericList_toET
#RepeatUntilSize.fromET = GenericList_fromET


def readArea(type):
    def checkArea(obj, lst, ctx):
        # print(ctx._io.tell(), (ctx.offset + ctx.size))
        return ctx._io.tell() >= (ctx.offset + ctx.size)

    return IfThenElse(this.size > 0,
                      Pointer(lambda foo: int(foo.offset), RepeatUntil(predicate=checkArea, subcon=type, check_predicate=False)),
                      Array(0, type)
                      )
