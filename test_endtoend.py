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

    ctx, size = T.fromET(context={}, parent=xml, name="Test", is_root=True)
    rebuild = T.build(ctx)

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

    ctx, size = T.fromET(context={}, parent=xml, name="Test", is_root=True)
    rebuild = T.build(ctx)

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

    ctx, size = T.fromET(context={}, parent=xml, name="Test", is_root=True)
    rebuild = T.build(ctx)

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

    ctx, size = T.fromET(context={}, parent=xml, name="Test", is_root=True)
    rebuild = T.build(ctx)

    assert(size == len(data))
    assert(data == rebuild)

def test_xml_string_array():
    T = Struct(
        "foo" / Enum(Int8ul, true=1, false=0),
        "entries" / Array(4, PaddedString(2, "utf-16-le")),
        )

    data = b"\x01\x65\x00\x66\x00\x67\x00\x68\x00"
    d = T.parse(data)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")
    assert(str == """<Test foo="true"><entries>e,f,g,h</entries></Test>""")

    ctx, size = T.fromET(context={}, parent=xml, name="Test", is_root=True)
    rebuild = T.build(ctx)

    assert(size == len(data))
    assert(data == rebuild)

def test_xml_array():
    T = Struct(
        "foo" / Enum(Int8ul, true=1, false=0),
        "entries" / Array(6, "int" / Int8ul),
        )

    data = b"\x01\x02\x00\x65\x00\x66\x00"
    d = T.parse(data)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")
    assert(str == """<Test foo="true"><entries>2,0,101,0,102,0</entries></Test>""")

    ctx, size = T.fromET(context={}, parent=xml, name="Test", is_root=True)
    rebuild = T.build(ctx)

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
    assert(str == """<Test foo="true"><test>2,0,101,0,102,0</test></Test>""")

    xml_rebuild, size, _ = T.fromET(xml, "Test", is_root=True)
    rebuild = T.build(xml_rebuild)

    assert(size == len(data))
    assert(data == rebuild)

def test_xml_rebuild_prefixed_array():
    T = Struct(
        "foo" / Enum(Int8ul, true=1, false=0),
        "test" / PrefixedArray(Int32ul, Int8ul),
        )

    data = b"\x01\x06\x00\x00\x00\x02\x00\x65\x00\x66\x00"
    d = T.parse(data)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")
    assert(str == """<Test foo="true"><test>2,0,101,0,102,0</test></Test>""")

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
    assert(str == """<Test foo="true" bar="true" baz="false"><test>2,3,4,5,6,0</test></Test>""")

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

def test_xml_if_array():
    T = Struct(
        "foo" / Enum(Int8ul, true=1, false=0),
        "baz" / Int8ul,
        "testarr" / If(this.foo == "true", Array(2, Int8ul))
    )

    data = b"\x01\x08\x00\x08"
    d = T.parse(data)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")

    xml_rebuild, size, _ = T.fromET(xml, "Test", is_root=True)
    rebuild = T.build(xml_rebuild)
    assert(rebuild == data)

def test_xml_array_array_if_unnamed():
    T = Struct(
        "foo" / Enum(Int8ul, true=1, false=0),
        "baz" / Int8ul,
        "testarr" / If(this.foo == "true", Array(2, Struct(
            "idx" / Rebuild(Int8ul, this._index),
            "t" / Int8ul,
            )))
    )

    data = b"\x01\x08\x00\x01\x01\x08"
    d = T.parse(data)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")

    xml_rebuild, size, _ = T.fromET(xml, "Test", is_root=True)
    rebuild = T.build(xml_rebuild)
    assert(rebuild == data)


def test_xml_array_rebuild_index():
    T = Struct(
        "foo" / Enum(Int8ul, true=1, false=0),
        "baz" / Int8ul,
        "testarr" / If(this.foo == "true", Array(2, "testdata" / Struct(
            "idx" / Rebuild(Int8ul, this._index),
            "t" / Int8ul,
        )))
    )

    data = b"\x01\x08\x00\x01\x01\x08"
    d = T.parse(data)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")

    xml_rebuild, size, _ = T.fromET(xml, "Test", is_root=True)
    rebuild = T.build(xml_rebuild)
    assert(rebuild == data)

def test_xml_lazybound():
    T = Struct(
        "foo" / Enum(Int8ul, true=1, false=0),
        "baz" / Int8ul,
        "bar" / If(this.foo == "true", LazyBound(lambda: T))
    )

    data = b"\x01\x08\x00\x08"
    d = T.parse(data)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")

    xml_rebuild, size, _ = T.fromET(xml, "Test", is_root=True)
    rebuild = T.build(xml_rebuild)
    assert(rebuild == data)

def test_xml_switch():
    T = Struct(
        "foo" / Int8ul,
        "baz" / Switch(this.foo, {
            0x00000001: "Int8" / Struct("value" / Int8ul),
            0x00000002: "Int32" / Struct("value" / Int32sl),
        }),
        "asd" / Switch(this.foo, {
            0x00000002: "testitem1" / Struct("value" / Int8ul),
            0x00000001: "testitem2" / Struct("value" / Int32sl),
        }),
    )

    data = b"\x01\x08\x00\x08\x20\x08"
    d = T.parse(data)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")
    assert(str == """<Test foo="1"><Int8 value="8" /><testitem2 value="136316928" /></Test>""")

    xml_rebuild, size, _ = T.fromET(xml, "Test", is_root=True)
    rebuild = T.build(xml_rebuild)
    assert(rebuild == data)

def test_xml_switch_nested():
    T = Struct(
        "foo" / Int8ul,
        "baz" / Switch(this.foo, {
            0x00000001: "Int8" / Struct("value" / Int8ul),
            0x00000002: "Int32" / Struct("asd" / Switch(this._.foo, {
                0x00000002: "testitem1" / Struct("value" / Int8ul),
                0x00000001: "testitem2" / Struct("value" / Int32sl),
            })),
        }),
        )

    data = b"\x02\x08"
    d = T.parse(data)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")
    assert(str == """<Test foo="2"><Int32><testitem1 value="8" /></Int32></Test>""")

    xml_rebuild, size, _ = T.fromET(xml, "Test", is_root=True)
    rebuild = T.build(xml_rebuild)
    assert(rebuild == data)

def test_xml_switch_rebuild():
    T = Struct(
        "foo" / Rebuild(Int8ul, this._switchid_baz),
        "baz" / Switch(this.foo, {
            0x00000001: "Int8" / Struct("value" / Int8ul),
            0x00000002: "Int32" / Struct("value" / Int32sl),
        }),
        "asd" / Switch(this.foo, {
            0x00000002: "testitem1" / Struct("value" / Int8ul),
            0x00000001: "testitem2" / Struct("value" / Int32sl),
        }),
        )

    data = b"\x01\x08\x00\x08\x20\x08"
    d = T.parse(data)

    xml = T.toET(d, name="Test", is_root=True)
    str = ET.tostring(xml).decode("utf-8")
    assert(str == """<Test><Int8 value="8" /><testitem2 value="136316928" /></Test>""")

    xml_rebuild, size, _ = T.fromET(xml, "Test", is_root=True)
    rebuild = T.build(xml_rebuild)
    assert(rebuild == data)
