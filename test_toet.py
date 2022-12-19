# tests for the construct xml toET stuff

import pytest

from cons_xml import *
from cons_utils import *

def test_formatfield_1():
    T = Int32ul,

    ctx = {"foo": 5}
    parent = ET.Element("parent")
    child = T[0].toET(context=ctx, name="foo", parent=parent)
    assert(child is None)
    assert(parent.attrib["foo"] == "5")

def test_renamed_1():
    T = "test" / Int32ul,

    ctx = {"foo": 5}
    parent = ET.Element("parent")
    child = T[0].toET(context=ctx, name="foo", parent=parent)
    assert(child is None)
    assert(parent.attrib["test"] == "5")

def test_create_child_context():
    ctx = {"bar": {"foo": 1, "bar": 3, "baz": 5}, "foobar": 5}
    child_ctx = create_child_context(context=ctx, name="bar")
    print(child_ctx)
    assert(child_ctx["_"]["foobar"] == 5)
    assert(child_ctx["bar"]["foo"] == 1)
    assert(child_ctx["bar"]["bar"] == 3)
    assert(child_ctx["bar"]["baz"] == 5)

def test_struct_formatfields():
    T = Struct(
        "a" / Int32ul,
        "b" / Float32l,
        )

    ctx = {"teststruct": {"a": 5, "b": 4.6}}
    child = T.toET(context=ctx, name="teststruct", parent=None)
    assert(child.attrib["a"] == "5")
    assert(child.attrib["b"] == "4.6")
