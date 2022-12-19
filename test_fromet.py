# tests for the construct xml fromET stuff

import pytest

from cons_xml import *
from cons_utils import *

def test_formatfield_1():
    T = Int32ul,
    ctx = {}
    parent = ET.Element("parent")
    parent.attrib["foo"] = "4"
    ctx, size = T[0].fromET(context=ctx, parent=parent, name="foo")
    assert(size == 4)
    assert(ctx["foo"] == 4)


def test_renamed_1():
    T = "test" / Int32ul,
    ctx = {}
    parent = ET.Element("parent")
    parent.attrib["test"] = 4
    ctx, size = T[0].fromET(context=ctx, parent=parent, name="foo")
    assert(size == 4)
    assert(ctx["test"] == 4)

    pass

def test_struct_formatfields():
    T = Struct(
        "a" / Int32ul,
        "b" / Float32l,
    )

    ctx = {"test": "someparentstuff"}

    parent = ET.Element("parent")
    struct = ET.Element("teststruct")
    struct.attrib["a"] = "3"
    struct.attrib["b"] = "4.6"
    parent.append(struct)

    ctx, size = T.fromET(context=ctx, parent=parent, name="teststruct", offset=56)
    assert(size == 8)
    assert(ctx["a"] == 3)
    assert(ctx["b"] == 4.6)
    assert(ctx["_offset"] == 56)
    assert(ctx["_size"] == 8)
    assert(ctx["_endoffset"] == 64)
    assert(ctx["_"]["test"] == "someparentstuff")

