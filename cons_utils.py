from io import BytesIO
import xml.etree.ElementTree as ET
from utils import compress_zlib, decompress_zlib
from cons_xml import *
import itertools


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
        ctx = create_context(context, "Compressed")
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

    def toET(self, context, name=None, parent=None):
        assert(isinstance(context[name], ListContainer))
        assert(parent is not None)

        i=0
        for item in context[name]:
            ctx = create_context(context, name, list_index=i)
            it = self.subcon.toET(context=ctx, name=name[:-5], parent=None)
            if it is not None:
                parent.append(it)
            i+=1

        return None


    def fromET(self, parent, name):
        elem = parent.attrib[name]

        assert(isinstance(elem, list))
        return [self.subcon.fromET(x) for x in elem]


def readArea(type):
    def checkArea(obj, lst, ctx):
        # print(ctx._io.tell(), (ctx.offset + ctx.size))
        return ctx._io.tell() >= (ctx.offset + ctx.size)

    return IfThenElse(this.size > 0,
                        Pointer(lambda foo: int(foo.offset), RepeatUntilSize(checkArea, type)),
                        Array(0, type)
                        )

