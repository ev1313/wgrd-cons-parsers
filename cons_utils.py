from io import BytesIO
import xml.etree.ElementTree as ET
from cons_xml import *
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


class ZLibCompressed(Tunnel):
    """ works exactly like Compressed, but with our zlib decompress function """

    def __init__(self, subcon):
        super().__init__(subcon)

    def _decode(self, data, context, path):
        pdb.set_trace()
        decompressed_data = decompress_zlib(data)
        self.decompressed_size = len(decompressed_data)
        return decompressed_data

    def _encode(self, data, context, path):
        self.decompressed_size = len(data)
        return compress_zlib(data)

    def toET(self, context, name=None, parent=None):
        elem = ET.Element("Compressed")
        pdb.set_trace()
        ctx = create_child_context(context, "Compressed")
        child = self.subcon.toET(context=ctx, name=name, parent=elem)
        if child is not None:
            elem.append(child)
        return elem

    def fromET(self, parent, name):
        assert(0)



class RepeatUntilSize(Subconstruct):
    def __init__(self, predicate, subcon, discard=False):
        super().__init__(subcon)
        self.predicate = predicate
        self.discard = discard

    def _parse(self, stream, context, path):
        predicate = self.predicate
        discard = self.discard
        if not callable(predicate):
            predicate = lambda _1, _2, _3: predicate
        obj = ListContainer()
        for i in itertools.count():
            context._index = i
            e = self.subcon._parsereport(stream, context, path)
            if not discard:
                obj.append(e)
            if predicate(e, obj, context):
                return obj

    def _build(self, obj, stream, context, path):
        discard = self.discard
        partiallist = ListContainer()
        retlist = ListContainer()
        for i, e in enumerate(obj):
            context._index = i
            buildret = self.subcon._build(e, stream, context, path)
            if not discard:
                retlist.append(buildret)
                partiallist.append(buildret)
        return retlist

    def _sizeof(self, context, path):
        raise SizeofError("cannot calculate size, amount depends on actual data", path=path)

    def _emitparse(self, code):
        fname = f"parse_repeatuntil_{code.allocateId()}"
        block = f"""
            def {fname}(io, this):
                list_ = ListContainer()
                while True:
                    obj_ = {self.subcon._compileparse(code)}
                    if not ({self.discard}):
                        list_.append(obj_)
                    if ({self.predicate}):
                        return list_
        """
        code.append(block)
        return f"{fname}(io, this)"

    def _emitbuild(self, code):
        fname = f"build_repeatuntil_{code.allocateId()}"
        block = f"""
            def {fname}(obj, io, this):
                objiter = iter(obj)
                list_ = ListContainer()
                while True:
                    obj_ = reuse(next(objiter), lambda obj: {self.subcon._compilebuild(code)})
                    list_.append(obj_)
                    if ({self.predicate}):
                        return list_
        """
        code.append(block)
        return f"{fname}(obj, io, this)"

    def _emitfulltype(self, ksy, bitwise):
        return dict(type=self.subcon._compileprimitivetype(ksy, bitwise), repeat="until",
                    repeat_until=repr(self.predicate).replace("obj_", "_"))


RepeatUntilSize.toET = GenericList_toET
RepeatUntilSize.fromET = GenericList_fromET

def readArea(type):
    def checkArea(obj, lst, ctx):
        # print(ctx._io.tell(), (ctx.offset + ctx.size))
        return ctx._io.tell() >= (ctx.offset + ctx.size)

    return IfThenElse(this.size > 0,
                        Pointer(lambda foo: int(foo.offset), RepeatUntilSize(checkArea, type)),
                        Array(0, type)
                        )

