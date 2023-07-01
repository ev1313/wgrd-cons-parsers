# tests for the dingsda xml fromET stuff

import pytest

from .cons_xml import *
from .cons_utils import *


def test_formatfield():
    T = Int32ul
    ctx = {}
    parent = ET.Element("parent")
    parent.attrib["foo"] = "4"
    ctx, size = T.fromET(context=ctx, parent=parent, name="foo")
    assert (size == 4)
    assert (ctx["foo"] == 4)

    ctx = {"foo": [2]}
    ctx, size = T.fromET(context=ctx, parent=parent, name="foo")
    assert (size == 4)
    assert (ctx["foo"] == [2, 4])


def test_renamed():
    T = "test" / Int32ul
    ctx = {"teststuff": "someparentstuff"}
    parent = ET.Element("parent")
    parent.attrib["test"] = 4
    ctx, size = T.fromET(context=ctx, parent=parent, name="foo")
    assert (size == 4)
    assert (ctx["teststuff"] == "someparentstuff")
    assert (ctx["test"] == 4)

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
    assert (size == 8)
    assert (ctx["test"] == "someparentstuff")
    assert (ctx["teststruct"]["a"] == 3)
    assert (ctx["teststruct"]["b"] == 4.6)
    assert (ctx["teststruct"]["_offset"] == 56)
    assert (ctx["teststruct"]["_size"] == 8)
    assert (ctx["teststruct"]["_endoffset"] == 64)


def test_struct_root():
    T = Struct(
        "a" / Int32ul,
        "b" / Float32l,
    )

    ctx = {"test": "someparentstuff"}

    struct = ET.Element("teststruct")
    struct.attrib["a"] = "3"
    struct.attrib["b"] = "4.6"

    ctx, size = T.fromET(context=ctx, parent=struct, name="teststruct", offset=56, is_root=True)
    assert (size == 8)
    assert (ctx["test"] == "someparentstuff")
    assert (ctx["a"] == 3)
    assert (ctx["b"] == 4.6)
    assert (ctx["_offset"] == 56)
    assert (ctx["_size"] == 8)
    assert (ctx["_endoffset"] == 64)


def test_struct_nested():
    T = Struct("foo" / Int32ul,
               "newname" / Struct(
                   "a" / Int32ul,
                   "b" / Float32l,
               ),
               "bar" / Int32ul,
               )

    ctx = {"test": "someparentstuff"}

    parent = ET.Element("parent")
    subparent = ET.Element("teststruct")
    subparent.attrib["foo"] = "12"
    struct = ET.Element("newname")
    struct.attrib["a"] = "3"
    struct.attrib["b"] = "4.6"
    subparent.attrib["bar"] = "13"
    subparent.append(struct)
    parent.append(subparent)

    ctx, size = T.fromET(context=ctx, parent=parent, name="teststruct", offset=56)
    assert (size == 16)
    assert (ctx["test"] == "someparentstuff")
    assert (ctx["teststruct"]["newname"]["a"] == 3)
    assert (ctx["teststruct"]["newname"]["b"] == 4.6)
    assert (ctx["teststruct"]["_offset"] == 56)
    assert (ctx["teststruct"]["_size"] == 16)
    assert (ctx["teststruct"]["_endoffset"] == 72)


def test_array_formatfields():
    T = Array(4, Int32ul)

    parent = ET.Element("parent")
    child = ET.Element("testarray")
    child.text = "4,3,2,1"
    parent.append(child)
    ctx = {"test": "someparentstuff"}
    ctx, size = T.fromET(context=ctx, parent=parent, name="testarray", offset=12)
    assert (size == 16)
    assert (ctx["test"] == "someparentstuff")
    assert (ctx["testarray"] == [4, 3, 2, 1])


# named formatfields in arrays should be ignored
def test_array_formatfields():
    T = Array(4, "foobar" / Int32ul)

    parent = ET.Element("parent")
    child = ET.Element("testarray")
    child.text = "4,3,2,1"
    parent.append(child)
    ctx = {"test": "someparentstuff"}
    ctx, size = T.fromET(context=ctx, parent=parent, name="testarray", offset=12)
    assert (size == 16)
    assert (ctx["test"] == "someparentstuff")
    assert (ctx["testarray"] == [4, 3, 2, 1])


def test_array_struct():
    T = Struct("foo" / Int32ul,
               "arr" / Array(4, Int32ul),
               "bar" / Int32ul,
               )
    parent = ET.Element("parent")
    child = ET.Element("teststruct")
    arr = ET.Element("arr")
    arr.text = "1,2,3,4"
    child.attrib["foo"] = "2"
    child.attrib["bar"] = "4"
    child.append(arr)
    parent.append(child)
    ctx = {"test": "someparentstuff"}
    ctx, size = T.fromET(context=ctx, parent=parent, name="teststruct", offset=12)
    assert (size == 6 * 4)
    assert (ctx["test"] == "someparentstuff")
    assert (ctx["teststruct"]["_size"] == size)
    assert (ctx["teststruct"]["_offset"] == 12)
    assert (ctx["teststruct"]["_endoffset"] == size + 12)
    assert (ctx["teststruct"]["arr"] == [1, 2, 3, 4])


def test_array_struct_nested():
    T = Struct("foo" / Int32ul,
               "arr" / Array(4, "teststr" / Struct(
                   "t" / Int8ul,
                   "w" / Int8ul,
               )),
               "bar" / Int32ul,
               )

    parent = ET.Element("parent")
    child = ET.Element("teststruct")
    arr = ET.Element("teststr")
    arr.attrib["t"] = "42"
    arr.attrib["w"] = "24"
    arr2 = ET.Element("teststr")
    arr2.attrib["t"] = "421"
    arr2.attrib["w"] = "241"
    child.attrib["foo"] = "2"
    child.attrib["bar"] = "4"
    child.append(arr)
    child.append(arr2)
    parent.append(child)
    ctx = {"test": "someparentstuff"}
    ctx, size = T.fromET(context=ctx, parent=parent, name="teststruct", offset=12)
    assert (ctx["test"] == "someparentstuff")
    assert (ctx["teststruct"]["foo"] == 2)
    assert (ctx["teststruct"]["arr"][0]["t"] == 42)
    assert (ctx["teststruct"]["arr"][0]["w"] == 24)
    assert (ctx["teststruct"]["arr"][1]["t"] == 421)
    assert (ctx["teststruct"]["arr"][1]["w"] == 241)
    assert (ctx["teststruct"]["bar"] == 4)

def test_ifthenelse():
    T = If(this.foo == 1, "foo" / Struct("x" / Int32ul))

    parent = ET.Element("parent")
    child = ET.Element("foo")
    child.attrib["x"] = "34"
    parent.append(child)

    ctx = {"test": "foobarbaz"}
    ctx, size = T.fromET(context=ctx, parent=parent, name="testname", offset=12)
    assert (ctx["test"] == "foobarbaz")
    assert (size == 4)
    assert (ctx["testname"]["_offset"] == 12)
    assert (ctx["testname"]["_size"] == 4)
    assert (ctx["testname"]["_endoffset"] == 16)
    assert (ctx["testname"]["x"] == 34)

    T = Struct("foo" / Int32ul,
               "ui32" / If(this.foo == 1, Int32ul),
               "ui16" / If(this.foo == 0, Int16ul),
               "baz" / Int32ul,
               )
    parent = ET.Element("parent")
    child = ET.Element("testname")
    child.attrib["foo"] = "1"
    child.attrib["ui16"] = "32"
    child.attrib["baz"] = "4"
    parent.append(child)
    ctx = {"test": "foobarbaz"}
    ctx, size = T.fromET(context=ctx, parent=parent, name="testname", offset=12)
    assert (ctx["test"] == "foobarbaz")
    assert (size == 10)
    assert (ctx["testname"]["_offset"] == 12)
    assert (ctx["testname"]["_size"] == 10)
    assert (ctx["testname"]["_endoffset"] == 22)


def test_named_ifthenelse():
    T = Struct("foo" / Int32ul,
               "ui32" / If(this.foo == 1, Struct("x" / Int32ul)),
               "ui16" / If(this.foo == 0, Struct("x" / Int16ul)),
               "baz" / Int32ul,
               )
    parent = ET.Element("parent")
    child = ET.Element("testname")
    child.attrib["foo"] = "1"
    ui16 = ET.Element("ui16")
    ui16.attrib["x"] = "32"
    child.attrib["baz"] = "4"
    child.append(ui16)
    parent.append(child)
    ctx = {"test": "foobarbaz"}
    ctx, size = T.fromET(context=ctx, parent=parent, name="testname", offset=12)
    assert (ctx["test"] == "foobarbaz")
    assert (size == 10)
    assert (ctx["testname"]["_offset"] == 12)
    assert (ctx["testname"]["_size"] == 10)
    assert (ctx["testname"]["_endoffset"] == 22)

    SwitchType = Struct(
    "typeId" / Rebuild(Int32ul, this._switchid_data),
    "data" / Switch(this.typeId, {
        0x00000000: "Boolean" / Struct("value" / Enum(Int8ul, false=0, true=1)),
        0x00000001: "Int8" / Struct("value" / Int8ul),
        0x00000002: "Int16" / Struct("value" / Int16ul),
    })
    )
    
    T = Struct("foo" / Int32ul,
               "ui32" / If(this.foo == 1, Int32ul),
               "ui16" / If(this.foo == 0, SwitchType),
               "baz" / Int32ul,
               )
    parent = ET.Element("parent")
    child = ET.Element("testname")
    child.attrib["foo"] = "1"
    ui16 = ET.Element("ui16")
    switch = ET.Element("Int16")
    switch.attrib["value"] = "32"
    ui16.append(switch)
    child.attrib["baz"] = "4"
    child.append(ui16)
    parent.append(child)
    ctx = {"test": "foobarbaz"}
    ctx, size = T.fromET(context=ctx, parent=parent, name="testname", offset=12)
    assert (ctx["test"] == "foobarbaz")
    assert (size == 14)
    assert (ctx["testname"]["_offset"] == 12)
    assert (ctx["testname"]["_size"] == 14)
    assert (ctx["testname"]["_endoffset"] == 26)


def test_focuseseq():
    T = FocusedSeq("foo", "one" / Rebuild(Int32ul, this.foo), "foo" / Int32ul, "two" / Rebuild(Int32ul, this.foo))

    parent = ET.Element("parent")
    parent.attrib["foo"] = "5"
    ctx = {"test": "foobarbaz"}
    ctx, size = T.fromET(context=ctx, parent=parent, name="foo", offset=13)
    assert (size == 12)
    assert (ctx["test"] == "foobarbaz")
    assert (ctx["foo"] == 5)

def test_rebuild():
    T = Struct("foo" / Int32ul,
               "one" / Rebuild(Int32ul, this.foo),
               "two" / Rebuild(Int32ul, lambda ctx: ctx.one)
        )

    parent = ET.Element("parent")
    child = ET.Element("foo")
    child.attrib["foo"] = "5"
    parent.append(child)
    ctx = {"test": "foobarbaz"}
    ctx, size = T.fromET(context=ctx, parent=parent, name="foo", offset=13)
    assert (size == 12)
    assert (ctx["test"] == "foobarbaz")
    assert (ctx["foo"]["foo"] == 5)
    assert (ctx["foo"]["one"] == None)
    assert (ctx["foo"]["two"] == None)

def test_prefixedarray_struct_nested():
    T = Struct("foo" / Int32ul,
               "arr" / PrefixedArray(Int32ul, "teststr" / Struct(
                   "t" / Int8ul,
                   "w" / Int8ul,
                   )),
               "bar" / Int32ul,
               )

    parent = ET.Element("parent")
    child = ET.Element("teststruct")
    arr = ET.Element("teststr")
    arr.attrib["t"] = "42"
    arr.attrib["w"] = "24"
    arr2 = ET.Element("teststr")
    arr2.attrib["t"] = "421"
    arr2.attrib["w"] = "241"
    child.attrib["foo"] = "2"
    child.attrib["bar"] = "4"
    child.append(arr)
    child.append(arr2)
    parent.append(child)
    ctx = {"test": "someparentstuff"}
    ctx, size = T.fromET(context=ctx, parent=parent, name="teststruct", offset=12)
    assert (ctx["test"] == "someparentstuff")
    assert (ctx["teststruct"]["foo"] == 2)
    assert (ctx["teststruct"]["arr"][0]["t"] == 42)
    assert (ctx["teststruct"]["arr"][0]["w"] == 24)
    assert (ctx["teststruct"]["arr"][1]["t"] == 421)
    assert (ctx["teststruct"]["arr"][1]["w"] == 241)
    assert (ctx["teststruct"]["bar"] == 4)

def test_lazybound():
    Foo = Struct("asd" / Int32ul,
                 "fgh" / Int32ul,)

    Test = Struct("foo" / Int32ul,
                  "test" / LazyBound(lambda: Foo),
                  "baz" / Int32ul,)

    parent = ET.Element("parent")
    child = ET.Element("teststruct")
    child.attrib["foo"] = 1
    child.attrib["baz"] = 2
    child_child = ET.Element("test")
    child_child.attrib["asd"] = 23
    child_child.attrib["fgh"] = 32
    child.append(child_child)
    parent.append(child)

    ctx = {"test": "someparentstuff"}
    ctx, size = Test.fromET(context=ctx, parent=parent, name="teststruct", offset=12)
    assert (ctx["test"] == "someparentstuff")
    assert (ctx["teststruct"]["foo"] == 1)
    assert (ctx["teststruct"]["baz"] == 2)
    assert(ctx["teststruct"]["test"]["asd"] == 23)
    assert(ctx["teststruct"]["test"]["fgh"] == 32)

def test_lazybound_array():
    Foo = Struct("asd" / Int32ul,
                 "fgh" / Int32ul,)

    Test = Struct("foo" / Int32ul,
                  "test" / PrefixedArray(Int32ul, "TestItem" / LazyBound(lambda: Foo)),
                  "baz" / Int32ul,)

    parent = ET.Element("parent")
    child = ET.Element("teststruct")
    child.attrib["foo"] = 1
    child.attrib["baz"] = 2
    child_child_1 = ET.Element("TestItem")
    child_child_1.attrib["asd"] = 23
    child_child_1.attrib["fgh"] = 32
    child_child_2 = ET.Element("TestItem")
    child_child_2.attrib["asd"] = 231
    child_child_2.attrib["fgh"] = 321
    child.append(child_child_1)
    child.append(child_child_2)
    parent.append(child)

    ctx = {"test": "someparentstuff"}
    ctx, size = Test.fromET(context=ctx, parent=parent, name="teststruct", offset=12)
    assert (ctx["test"] == "someparentstuff")
    assert (ctx["teststruct"]["foo"] == 1)
    assert (ctx["teststruct"]["baz"] == 2)
    assert(ctx["teststruct"]["test"][0]["asd"] == 23)
    assert(ctx["teststruct"]["test"][0]["fgh"] == 32)
    assert(ctx["teststruct"]["test"][1]["asd"] == 231)
    assert(ctx["teststruct"]["test"][1]["fgh"] == 321)


def test_switch():
    TestType = Struct("foo" / Int32ul,
               "test" / Switch(this.foo,
                               {
                                   0x0: "Boolean" / Struct("value" / Enum(Int8ul, false=0, true=1)),
                                   0x1: "String" / Struct("value" / PascalString(Int32ul, "utf-16")),
                                   0x2: "Test" / Struct("value" / LazyBound(lambda: TestType)),
                                   0x3: "TestArray" / PrefixedArray(Int32ul, "TestItem" / LazyBound(lambda: TestType)),
                               }
               ),
               "baz" / Int32ul)