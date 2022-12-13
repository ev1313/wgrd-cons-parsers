#!/usr/bin/env python3

import pdb
from io import BytesIO
import xml.etree.ElementTree as ET
from construct import *


def evaluate(param, context):
    return param(context) if callable(param) else param


def create_context(context, name, list_index=None, is_root=False):
    if not is_root:
        assert (context is not None)
        assert (name is not None)
    else:
        return context

    if isinstance(context[name], Container):
        ctx = Container(_=context, **context[name])
    elif isinstance(context[name], ListContainer):
        assert (list_index is not None)
        ctx = Container(_=context)
        ctx._index = list_index
        ctx[list_index] = context[name][list_index]
    else:
        ctx = Container(_=context)
        ctx[name] = context[name]

    return ctx


def Renamed_toET(self, context, name=None, parent=None):
    # corner case with Switch e.g.
    if name != self.name:
        ctx = context
        ctx[self.name] = context[name]
        ctx[name] = None
    else:
        ctx = context
    return self.subcon.toET(context=context, name=self.name, parent=parent)


def Renamed_fromET(self, parent, name, is_root=False):
    return self.subcon.fromET(parent=parent, name=self.name, is_root=is_root)


Renamed.toET = Renamed_toET
Renamed.fromET = Renamed_fromET


def Struct_toET(self, context, name=None, parent=None, is_root=False):
    ctx = create_context(context, name, is_root=is_root)

    if name is None:
        name = "Struct"
        assert (0)

    elem = ET.Element(name)
    for sc in self.subcons:
        if sc.name is None or sc.name.startswith("_"):
            continue


        child = sc.toET(context=ctx, name=sc.name, parent=elem)
        if child is not None:
            elem.append(child)

    return elem


def Struct_fromET(self, parent, name, is_root=False):
    if not is_root:
        elem = parent.findall(name)
    else:
        elem = parent
        assert(elem.tag == name)

    ret = Container()
    size = 0

    for sc in self.subcons:
        data, child_size = sc.fromET(elem, sc.name)
        size += child_size
        if data is not None:
            ret[sc.name] = data

    return ret, size


Struct.toET = Struct_toET
Struct.fromET = Struct_fromET


def FormatField_toET(self, context, name=None, parent=None):
    if name is None:
        assert (0)
    if parent is None:
        parent = ET.Element(name)

    parent.attrib[name] = str(context[name])
    if parent is None:
        return parent
    return None


def FormatField_fromET(self, parent, name, is_root=False):
    elem = parent.attrib[name]

    assert (len(self.fmtstr) == 2)
    if self.fmtstr[1] in ["B", "H", "L", "Q", "b", "h", "l", "q"]:
        return int(elem), self.size
    elif self.fmtstr[1] in ["e", "f", "d"]:
        return float(elem), self.size

    assert (0)


FormatField.toET = FormatField_toET
FormatField.fromET = FormatField_fromET


def Enum_toET(self, context, name=None, parent=None):
    # FIXME: only works for FormatFields
    return self.subcon.toET(context, name=name, parent=parent)


def Enum_fromET(self, parent, name, is_root=False):
    # FIXME: only works for FormatFields
    elem = parent.attrib[name]

    mapping = self.encmapping.get(elem, None)

    if mapping is None:
        return self.subcon.fromET(elem)
    else:
        return mapping, self.subcon.size


Enum.toET = Enum_toET
Enum.fromET = Enum_fromET

def Bytes_toET(self, context, name=None, parent=None):
    if name is None:
        assert (0)
    if parent is None:
        parent = ET.Element(name)

    assert(isinstance(context[name], bytes))
    parent.attrib[name] = context[name].hex()
    if parent is None:
        return parent
    return None


def Bytes_fromET(self, parent, name, is_root=False):
    elem = parent.attrib[name]
    b = b"".fromhex(elem)
    return b, len(b)


Bytes.toET = Bytes_toET
Bytes.fromET = Bytes_fromET


def StringEncoded_toET(self, context, name=None, parent=None):
    if name is None:
        assert (0)
    if parent is None:
        parent = ET.Element(name)

    parent.attrib[name] = context[name]
    if parent is None:
        return parent
    return None


def StringEncoded_fromET(self, parent, name, is_root=False):
    elem = parent.attrib[name]
    return elem, self.length


StringEncoded.toET = StringEncoded_toET
StringEncoded.fromET = StringEncoded_fromET


def IfThenElse_toET(self, context, name=None, parent=None):
    assert (context is not None)

    if(self.elsesubcon.__class__.__name__ != "Pass"):
        assert(self.thensubcon.__class__.__name__ == "Renamed")
        assert(self.elsesubcon.__class__.__name__ == "Renamed")
        assert(self.thensubcon.name != self.elsesubcon.name)

    c = evaluate(self.condfunc, context)
    if c:
        return self.thensubcon.toET(context=context, name=name, parent=parent)
    else:
        return self.elsesubcon.toET(context=context, name=name, parent=parent)


def IfThenElse_fromET(self, parent, name, is_root=False):
    elem = parent.attrib[name]

    if isinstance(self.elsesubcon, Array):
        assert(self.elsesubcon.count == 0)
    elif self.elsesubcon.__class__.__name__ == "Pass":
        pass
    else:
        assert(0)

    if len(elem) == 0:
        return self.elsesubcon.fromET(elem)
    return self.thensubcon.fromET(elem)


IfThenElse.toET = IfThenElse_toET
IfThenElse.fromET = IfThenElse_fromET


def Switch_toET(self, context, name=None, parent=None):
    key = evaluate(self.keyfunc, context)
    case = self.cases[key]
    return case.toET(context, name=name, parent=parent)


def Switch_fromET(self, parent, name, is_root=False):
    elem = parent.attrib[name]

    for case in self.cases:
        if case.name == elem.tag:
            return case.fromET(elem)


Switch.toET = Switch_toET
Switch.fromET = Switch_fromET


def Ignore_toET(self, context, name=None, parent=None):
    # does not need to be in the XML (will be rebuilt)
    return None


def Ignore_fromET(self, parent, name, is_root=False):
    # not required in dict, as it will be rebuilt
    return None


Rebuild.toET = Ignore_toET
Rebuild.fromET = Ignore_fromET
Const.toET = Ignore_toET
Const.fromET = Ignore_fromET

def IgnoreCls_toET(context, name=None, parent=None):
    # does not need to be in the XML (will be rebuilt)
    return None


def IgnoreCls_fromET(parent, name, is_root=False):
    # not required in dict, as it will be rebuilt
    return None


Tell.toET = IgnoreCls_toET
Tell.fromET = IgnoreCls_fromET
Pass.toET = IgnoreCls_toET
Pass.fromET = IgnoreCls_fromET


def Pointer_toET(self, context, name=None, parent=None):
    return self.subcon.toET(context=context, name=name, parent=parent)


def Pointer_fromET(self, parent, name, is_root=False):
    return self.subcon.fromET(parent=parent, name=name, is_root=is_root)


Pointer.toET = Pointer_toET
Pointer.fromET = Pointer_fromET

def GenericList_toET(self, context, name=None, parent=None):
    assert (isinstance(context[name], ListContainer))
    assert(name is not None)
    assert(parent is not None)
    i = 0
    for item in context[name]:
        ctx = create_context(context, name, list_index=i)
        it = self.subcon.toET(context=ctx, name=i, parent=None)
        if it is not None:
            parent.append(it)
        else:
            assert(0)
        i += 1

    return None


def GenericList_fromET(self, parent, name, is_root=False):
    name = self.subcon.name
    elems = parent.findall(name)
    pdb.set_trace()
    return [self.subcon.fromET(parent=x, name=name, is_root=True) for x in elems]


Array.toET = GenericList_toET
Array.fromET = GenericList_fromET

RepeatUntil.toET = GenericList_toET
RepeatUntil.fromET = GenericList_fromET


def LazyBound_toET(self, context, name=None, parent=None):
    sc = self.subconfunc()
    return sc.toET(context=context, name=name, parent=parent)


def LazyBound_fromET(self, parent, name, is_root=False):
    elem = parent.attrib[name]

    sc = self.subconfunc()
    return sc.fromET(elem)


LazyBound.toET = LazyBound_toET
LazyBound.fromET = LazyBound_fromET

Magic = Const

if __name__ == "__main__":
    Test = Struct(
        Tell,
        "foo" / Int32ul,
        "bar" / Enum(Int32ul, foo=0),
        "asdf" / Rebuild(Int32ul, lambda x: x.foo),
        "baz" / Rebuild(Int32ul, this.bar),
        "ptr" / Pointer(4, Struct("ptrobj" / Int16ul))
    )

    empty = b"\x00\x01\x02\x03\x04" * 100
    d = Test.parse(empty)

    xml = Test.toET(d, name="Test")
    ET.indent(xml, space="  ", level=0)
    str = ET.tostring(xml).decode("utf-8")
    print(str)

    x = Test.fromET(xml, "Test", is_root=True)
    print(x)
    print(Test.build(x))
