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

    xml_rebuild, size, _ = T.fromET(xml, "Test", is_root=True)
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

    xml_rebuild, size, _ = T.fromET(xml, "Test", is_root=True)
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

    xml_rebuild, size, _ = T.fromET(xml, "Test", is_root=True)
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

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")
    assert(str == """<Test foo="true"><str data="ef" /></Test>""")

    xml_rebuild, size, _ = T.fromET(xml, "Test", is_root=True)
    rebuild = T.build(xml_rebuild)

    assert(size == len(data))
    assert(data == rebuild)

def test_xml_array():
    T = Struct(
        "foo" / Enum(Int8ul, true=1, false=0),
        "test" / Array(6, "int" / Int8ul),
        )

    data = b"\x01\x02\x00\x65\x00\x66\x00"
    d = T.parse(data)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")
    assert(str == """<Test foo="true"><int int="2" /><int int="0" /><int int="101" /><int int="0" /><int int="102" /><int int="0" /></Test>""")

    xml_rebuild, size, _ = T.fromET(xml, "Test", is_root=True)
    pdb.set_trace()
    rebuild = T.build(xml_rebuild)

    assert(size == len(data))
    assert(data == rebuild)

def test_xml_rebuild_array():
    T = Struct(
        "foo" / Enum(Int8ul, true=1, false=0),
        "size" / Rebuild(Int16ul, lambda ctx: ctx._size_test),
        "test" / Array(this.size, "int" / Int8ul),
        )

    data = b"\x01\x06\x00\x02\x00\x65\x00\x66\x00"
    d = T.parse(data)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")
    assert(str == """<Test foo="true"><int int="2" /><int int="0" /><int int="101" /><int int="0" /><int int="102" /><int int="0" /></Test>""")

    xml_rebuild, size, _ = T.fromET(xml, "Test", is_root=True)
    rebuild = T.build(xml_rebuild)

    assert(size == len(data))
    assert(data == rebuild)


def test_xml_rebuild_repeatuntil():
    T = Struct(
        "foo" / Enum(Int8ul, true=1, false=0),
        "size" / Rebuild(Int16ul, lambda ctx: ctx._size_test),
        "test" / RepeatUntil(lambda obj, lst, ctx: obj == 0, "int" / Int8ul),
        "bar" / Enum(Int8ul, true=1, false=0),
        "baz" / Enum(Int8ul, true=1, false=0),
        )

    data = b"\x01\x06\x00\x02\x03\x04\x05\x06\x00\x01\x00"
    d = T.parse(data)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")
    assert(str == """<Test foo="true" bar="true" baz="false"><int int="2" /><int int="3" /><int int="4" /><int int="5" /><int int="6" /><int int="0" /></Test>""")

    xml_rebuild, size, _ = T.fromET(xml, "Test", is_root=True)

    assert(xml_rebuild["_offset_foo"] == 0)
    assert(xml_rebuild["_size_foo"] == 1)
    assert(xml_rebuild["_offset_size"] == xml_rebuild["_size_foo"])
    assert(xml_rebuild["_size_test"] == 6)
    assert(xml_rebuild["_offset_baz"] == 10)
    rebuild = T.build(xml_rebuild)

    assert(size == len(data))
    assert(data == rebuild)

def test_xml_pointer():
    T = Struct(
        "foo" / Enum(Int8ul, true=1, false=0),
        "offset" / Int16ul,
        "size" / Int16ul,
        "test" / Pointer(this.offset, "s" / Struct(
            "a1" / Int8ul,
            "a2" / Int8ul,
        ))
        )

    data = b"\x01\x08\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08"
    d = T.parse(data)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")

    xml_rebuild, size, _ = T.fromET(xml, "Test", is_root=True)
    rebuild = T.build(xml_rebuild)

    assert(xml_rebuild["_offset_test"] == 5)
    assert(xml_rebuild["test"]["_offset_a1"] == 0)
    assert(xml_rebuild["test"]["_offset_a2"] == 1)
    assert(xml_rebuild["_ptrsize_test"] == 2)
