# tests for the construct xml toET stuff

import pytest

from cons_xml import *
from cons_utils import *


def test_formatfield_1():
    T = Int32ul

    ctx = {"foo": 5}
    parent = ET.Element("parent")
    child = T.toET(context=ctx, name="foo", parent=parent)
    assert (child is None)
    assert (parent.attrib["foo"] == "5")


def test_renamed_1():
    T = "test" / Int32ul

    ctx = {"foo": 5}
    parent = ET.Element("parent")
    child = T.toET(context=ctx, name="foo", parent=parent)
    assert (child is None)
    assert (parent.attrib["test"] == "5")


def test_create_child_context():
    ctx = {"bar": {"foo": 1, "bar": 3, "baz": 5}, "foobar": 5}
    child_ctx = create_child_context(context=ctx, name="bar")
    assert (child_ctx["_"]["foobar"] == 5)
    assert (child_ctx["foo"] == 1)
    assert (child_ctx["bar"] == 3)
    assert (child_ctx["baz"] == 5)

    ctx = {"bar": ["foo", "bar", "baz"], "foobar": 5}
    child_ctx = create_child_context(context=ctx, name="bar", list_index=0)
    assert (child_ctx["_index"] == 0)
    assert (child_ctx["bar_0"] == "foo")


def test_struct_formatfields():
    T = Struct(
        "a" / Int32ul,
        "b" / Float32l,
    )

    ctx = {"teststruct": {"a": 5, "b": 4.6}}
    child = T.toET(context=ctx, name="teststruct", parent=None)
    assert (child.attrib["a"] == "5")
    assert (child.attrib["b"] == "4.6")


def test_struct_renamed():
    T = "newname" / Struct(
        "a" / Int32ul,
        "b" / Float32l,
    )

    ctx = {"teststruct": {"a": 5, "b": 4.6}}
    child = T.toET(context=ctx, name="teststruct", parent=None)
    assert (child.attrib["a"] == "5")
    assert (child.attrib["b"] == "4.6")


def test_struct_nested():
    T = Struct("foo" / Int32ul,
               "newname" / Struct(
                   "a" / Int32ul,
                   "b" / Float32l,
               ),
               "bar" / Int32ul,
               )

    ctx = {"teststruct": {"foo": 1, "newname": {"a": 5, "b": 4.6}, "bar": 45}}
    child = T.toET(context=ctx, name="teststruct", parent=None)
    assert (child.find("newname").attrib["a"] == "5")
    assert (child.find("newname").attrib["b"] == "4.6")
    str = ET.tostring(child).decode("utf-8")
    assert (str == """<teststruct foo="1" bar="45"><newname a="5" b="4.6" /></teststruct>""")


def test_array_formatfields():
    T = Array(4, Int32ul)

    parent = ET.Element("test")
    ctx = {"testarray": [1, 2, 3, 4]}
    child = T.toET(context=ctx, name="testarray", parent=parent)
    assert (child is None)
    items = parent.findall("testarray")
    assert (len(items) == 1)
    assert (items[0].text == "1,2,3,4")

    T = Array(4, "testname" / Int32ul)

    parent = ET.Element("test")
    ctx = {"testarray": [1, 2, 3, 4]}
    child = T.toET(context=ctx, name="testarray", parent=parent)
    assert (child is None)
    items = parent.findall("testarray")
    assert (len(items) == 1)
    assert (items[0].text == "1,2,3,4")


def test_array_in_struct():
    T = Struct("foo" / Int32ul,
               "arr" / Array(4, Int32ul),
               "bar" / Int32ul,
               )

    ctx = {"teststruct": {"foo": 1, "arr": [1, 2, 3, 4], "bar": 45}}
    child = T.toET(context=ctx, name="teststruct", parent=None)
    items = child.findall("arr")
    assert (len(items) == 1)
    assert (items[0].text == "1,2,3,4")


def test_array_struct():
    T = Array(4, Struct("x" / Int32ul,
                        "y" / Int32ul))

    parent = ET.Element("parent")
    ctx = {"testarr": [{"x": 1, "y": 1}, {"x": 2, "y": 2}]}
    child = T.toET(context=ctx, name="testarr", parent=parent)
    assert (child is None)
    items = parent.findall("testarr")
    assert (len(items) == 2)
    assert (items[0].attrib["x"] == "1")
    assert (items[0].attrib["y"] == "1")
    assert (items[1].attrib["x"] == "2")
    assert (items[1].attrib["y"] == "2")


def test_array_named_struct():
    T = Array(4, "NamedTest" / Struct("x" / Int32ul,
                                      "y" / Int32ul))

    parent = ET.Element("parent")
    ctx = {"testarr": [{"x": 1, "y": 1}, {"x": 2, "y": 2}]}
    child = T.toET(context=ctx, name="testarr", parent=parent)
    assert (child is None)
    items = parent.findall("NamedTest")
    assert (len(items) == 2)
    assert (items[0].attrib["x"] == "1")
    assert (items[0].attrib["y"] == "1")
    assert (items[1].attrib["x"] == "2")
    assert (items[1].attrib["y"] == "2")


def test_array_nested_struct():
    T = Struct("foo" / Int32ul,
               "arr" / Array(4, "NamedTest" / Struct(
                   "x" / Int32ul,
                   "y" / Int32ul)),
               "bar" / Int32ul,
               )

    parent = ET.Element("parent")
    ctx = {"testarr": {"foo": 1, "arr": [{"x": 1, "y": 1}, {"x": 2, "y": 2}], "bar": 2}}
    child = T.toET(context=ctx, name="testarr", parent=parent)
    items = child.findall("NamedTest")
    assert (len(items) == 2)
    assert (items[0].attrib["x"] == "1")
    assert (items[0].attrib["y"] == "1")
    assert (items[1].attrib["x"] == "2")
    assert (items[1].attrib["y"] == "2")


def test_const_struct():
    T = Struct("foo" / Int32ul,
               "bar" / Const(4, Int32ul),
               "baz" / Const(b"asdfg"),
               )

    parent = ET.Element("parent")
    ctx = {"teststruct": {"foo": 1, "bar": 4}}
    child = T.toET(context=ctx, name="teststruct", parent=parent)
    assert (child.attrib.get("bar", None) is None)
    assert (child.attrib.get("baz", None) is None)
    assert (child.attrib["foo"] == "1")

def test_ifthenelse():
    T = If(this.foo == 1, "foo" / Struct("x"/ Int32ul))

    parent = ET.Element("parent")
    ctx = {"foo": 1, "test": {"x": 42}}
    child = T.toET(context=ctx, parent=parent, name="test")
    assert(child.tag == "foo")
    assert(child.attrib["x"] == "42")

    ctx = {"foo": 2, "test": {"x": 42}}
    child = T.toET(context=ctx, parent=parent, name="test")
    assert(child is None)

def test_ifthenelse_in_struct():
    T = Struct("foo" / Int32ul,
               "bar" / IfThenElse(this.foo == 1, "bar_foostruct" / Struct("x" / Int32ul), "bar_barstruct" / Struct("y" / Int16ul)),
               "bar2" / IfThenElse(this.foo == 0, "bar2_foostruct" / Struct("x" / Int32ul), "bar2_barstruct" / Struct("y" / Int16ul)),
               "baz" / Int32ul,
    )
    parent = ET.Element("parent")
    ctx = {"teststruct": {"foo": 1, "bar": {"x": 1}, "bar2": {"y": 2}, "baz": 4}}
    child = T.toET(context=ctx, name="teststruct", parent=parent)
    assert (child.attrib["foo"] == "1")
    assert (child.attrib["baz"] == "4")
    bar = child.findall("bar_foostruct")
    assert(len(bar) == 1)
    assert(bar[0].attrib["x"] == "1")
    bar2 = child.findall("bar2_barstruct")
    assert(len(bar2) == 1)
    assert(bar2[0].attrib["y"] == "2")

    T = Struct("foo" / Int32ul,
               "ui32" / If(this.foo == 1, Int32ul),
               "ui16" / If(this.foo == 0, Int16ul),
               "baz" / Int32ul,
               )
    parent = ET.Element("parent")
    ctx = {"teststruct": {"foo": 1, "ui32": 23, "baz": 4}}
    child = T.toET(context=ctx, name="teststruct", parent=parent)
    assert (child.attrib["foo"] == "1")
    assert (child.attrib["ui32"] == "23")
    assert (child.attrib["baz"] == "4")
