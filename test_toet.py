# tests for the construct xml toET stuff

import pytest

from cons_xml import *
from cons_utils import *

def test_formatfield_1():
    T = Int32ul

    ctx = {"foo": 5}
    parent = ET.Element("parent")
    child = T.toET(context=ctx, name="foo", parent=parent)
    assert(child is None)
    assert(parent.attrib["foo"] == "5")

def test_renamed_1():
    T = "test" / Int32ul

    ctx = {"foo": 5}
    parent = ET.Element("parent")
    child = T.toET(context=ctx, name="foo", parent=parent)
    assert(child is None)
    assert(parent.attrib["test"] == "5")

def test_create_child_context():
    ctx = {"bar": {"foo": 1, "bar": 3, "baz": 5}, "foobar": 5}
    child_ctx = create_child_context(context=ctx, name="bar")
    assert(child_ctx["_"]["foobar"] == 5)
    assert(child_ctx["foo"] == 1)
    assert(child_ctx["bar"] == 3)
    assert(child_ctx["baz"] == 5)

    ctx = {"bar": ["foo", "bar", "baz"], "foobar": 5}
    child_ctx = create_child_context(context=ctx, name="bar", list_index=0)
    assert(child_ctx["_index"] == 0)
    assert(child_ctx["bar_0"] == "foo")

def test_struct_formatfields():
    T = Struct(
        "a" / Int32ul,
        "b" / Float32l,
        )

    ctx = {"teststruct": {"a": 5, "b": 4.6}}
    child = T.toET(context=ctx, name="teststruct", parent=None)
    assert(child.attrib["a"] == "5")
    assert(child.attrib["b"] == "4.6")

def test_struct_renamed():
    T = "newname" / Struct(
        "a" / Int32ul,
        "b" / Float32l,
        )

    ctx = {"teststruct": {"a": 5, "b": 4.6}}
    child = T.toET(context=ctx, name="teststruct", parent=None)
    assert(child.attrib["a"] == "5")
    assert(child.attrib["b"] == "4.6")

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
    assert(child.find("newname").attrib["a"] == "5")
    assert(child.find("newname").attrib["b"] == "4.6")
    str = ET.tostring(child).decode("utf-8")
    assert(str == """<teststruct foo="1" bar="45"><newname a="5" b="4.6" /></teststruct>""")

def test_array_formatfields():
    T = Array(4, Int32ul)

    parent=ET.Element("test")
    ctx = {"testarray": [1,2,3,4]}
    child = T.toET(context=ctx, name="testarray", parent=parent)
    assert(child is None)
    items = parent.findall("testarray")
    assert(len(items) == 1)
    assert(items[0].text == "1,2,3,4")