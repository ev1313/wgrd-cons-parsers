# tests for the construct xml stuff

import pytest

from cons_xml import *
from cons_utils import *

def test_xml_simple():
    T = Struct(
        "foo" / Const(18, Int8ul),
        "bar" / Int16ul,
        "baz" / Int16ub,
        "asd" / Int32ul,
    )

    data = b"\x12\x32\x42\x42\x32\x02\x00\x00\x00"
    d = T.parse(data)

    assert(d.foo == 18)
    assert(d.bar == 16946)
    assert(d.baz == 16946)
    assert(d.asd == 2)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")
    assert(str == """<Test bar="16946" baz="16946" asd="2" />""")

    xml_rebuild, size = T.fromET(xml, "Test", is_root=True)
    rebuild = T.build(xml_rebuild)

    assert(data == rebuild)
    assert(size == 9)

def test_xml_enum():
    T = Struct(
        "foo" / Enum(Int8ul, true=1, false=0),
        "bar" / Enum(Int16ul, foo=1, bar=2),
        "baz" / Enum(Int16ub, foo=1, bar=16946),
        "asd" / Int32ul,
        )

    data = b"\x01\x32\x42\x42\x32\x02\x00\x00\x00"
    d = T.parse(data)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")
    assert(str == """<Test foo="true" bar="16946" baz="bar" asd="2" />""")

    xml_rebuild, size = T.fromET(xml, "Test", is_root=True)
    rebuild = T.build(xml_rebuild)

    assert(data == rebuild)
    assert(size == 9)

def test_xml_ifthenelse():
    T = Struct(
        "foo" / Enum(Int8ul, true=1, false=0),
        "bar" / Enum(Int16ul, foo=1, bar=2),
        "baz" / Enum(Int16ub, foo=1, bar=16946),
        "asd" / If(lambda ctx: ctx.foo == "true", Int32ul),
        "xyz" / If(lambda ctx: ctx.foo == "false", Int32ub),
        )

    data = b"\x01\x03\x00\x42\x32\x02\x00\x00\x00"
    d = T.parse(data)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")
    assert(str == """<Test foo="true" bar="3" baz="bar" asd="2" />""")

    xml_rebuild, size = T.fromET(xml, "Test", is_root=True)
    rebuild = T.build(xml_rebuild)

    assert(size == 9)
    assert(data == rebuild)

def test_xml_rebuild():
    T = Struct(
        "foo" / Enum(Int8ul, true=1, false=0),
        "length" / Rebuild(Int16ul, lambda ctx: int(ctx.str._size / 2)),
        "str" / Struct(
            "data" / PaddedString(this._.length*2, "utf-16-le")
            ),
        )

    data = b"\x01\x02\x00\x65\x00\x66\x00"
    d = T.parse(data)
    print(d)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")
    assert(str == """<Test foo="true"><str data="ef" /></Test>""")

    xml_rebuild, size = T.fromET(xml, "Test", is_root=True)
    rebuild = T.build(xml_rebuild)

    assert(size == len(data))
    assert(data == rebuild)
