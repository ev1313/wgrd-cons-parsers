#!/usr/bin/env python3

import pdb

# used for building / parsing string arrays
from io import StringIO
import csv

import xml.etree.ElementTree as ET
from construct import *


def evaluate(param, context):
    return param(context) if callable(param) else param


def create_child_context(context, name, list_index=None, is_root=False):
    if not is_root:
        assert (context is not None)
        assert (name is not None)
    else:
        return context

    data = get_current_field(context, name)

    if isinstance(data, Container) or isinstance(data, dict):
        ctx = Container(_=context, **data)
    elif isinstance(data, ListContainer) or isinstance(data, list):
        assert (list_index is not None)
        # construct does not add an additional _ layer for arrays
        ctx = Container(**context)
        ctx._index = list_index
        ctx[f"{name}_{list_index}"] = data[list_index]
    else:
        # this is needed when the item is part of a list
        # then the name is e.g. "bar_1"
        ctx = Container(_=context)
        ctx[name] = data

    return ctx


def get_current_field(context, name):
    idx = context.get("_index", None)
    if idx is not None:
        return context[f"{name}_{idx}"]
    else:
        return context[name]


def rename_in_context(context, name, new_name):
    ctx = context
    idx = context.get("_index", None)
    if idx is not None:
        ctx[f"{new_name}_{idx}"] = context[f"{name}_{idx}"]
        ctx[f"{name}_{idx}"] = None
    else:
        ctx[new_name] = context[name]
        ctx[name] = None

    return ctx


def Renamed_toET(self, context, name=None, parent=None, is_root=False):
    ctx = context
    # corner case with Switch e.g.
    if name != self.name:
        ctx = rename_in_context(context=context, name=name, new_name=self.name)

    return self.subcon.toET(context=ctx, name=self.name, parent=parent, is_root=is_root)


def Renamed_fromET(self, context, parent, name, offset=0, is_root=False):
    return self.subcon.fromET(context=context, parent=parent, name=self.name, offset=offset, is_root=is_root)


Renamed.toET = Renamed_toET
Renamed.fromET = Renamed_fromET


def Struct_toET(self, context, name=None, parent=None, is_root=False):
    ctx = create_child_context(context, name, is_root=is_root)

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


def Struct_fromET(self, context, parent, name, offset=0, is_root=False):
    # we go down one layer
    ctx = Container()
    ctx["_"] = context

    # get the xml element
    if not is_root:
        elem = parent.findall(name)
        if len(elem) == 1:
            elem = elem[0]
    else:
        elem = parent
        assert (parent.tag == name)

    size = 0
    ctx["_offset"] = offset

    for sc in self.subcons:
        ctx, child_size = sc.fromET(context=ctx, parent=elem, name=sc.name, offset=offset)
        size += child_size
        ctx[f"_offset_{sc.name}"] = offset
        ctx[f"_size_{sc.name}"] = child_size
        offset += child_size
        ctx[f"_endoffset_{sc.name}"] = offset

    ctx["_size"] = size
    ctx["_endoffset"] = offset

    return ctx, size


Struct.toET = Struct_toET
Struct.fromET = Struct_fromET


def FocusedSeq_toET(self, context, name=None, parent=None, is_root=False):
    assert(isinstance(self.parsebuildfrom, str))
    for sc in self.subcons:
        if sc.name == self.parsebuildfrom:
            # FocusedSeq has to ignore the Rename
            # because e.g. PrefixedArray adds custom names
            if sc.__class__.__name__ == "Renamed":
                sc = sc.subcon
            else:
                assert(0)
            return sc.toET(context=context, name=name, parent=parent)
    assert(0)


def FocusedSeq_fromET(self, context, parent, name, offset=0, is_root=False):
    ctx = {"_": context}
    size = 0
    ctx["_offset"] = offset

    s = None
    for sc in self.subcons:
        size += s.sizeof()
        if sc.name == self.parsebuildfrom:
            assert(sc.__class__.__name__ == "Renamed")
            s = sc.subcon
            ctx, childsize = s.fromET(context=ctx, parent=parent, name=name, offset=offset, is_root=False)
            size += childsize

    assert(s is not None)

    ctx["_size"] = size

    return ctx, size+4

    assert (0)


FocusedSeq.toET = FocusedSeq_toET
FocusedSeq.fromET = FocusedSeq_fromET


def FormatField_toET(self, context, name=None, parent=None, is_root=False):
    assert (name is not None)
    data = str(get_current_field(context, name))

    if parent is None:
        return data

    parent.attrib[name] = data
    return None


def FormatField_fromET(self, context, parent, name, offset=0, is_root=False):
    if isinstance(parent, ET.Element):
        elem = parent.attrib[name]
    elif isinstance(parent, str):
        elem = parent
        assert(0)
    else:
        assert (0)

    assert (len(self.fmtstr) == 2)
    if self.fmtstr[1] in ["B", "H", "L", "Q", "b", "h", "l", "q"]:
        context[name] = int(elem)
        return context, self.length
    elif self.fmtstr[1] in ["e", "f", "d"]:
        context[name] = float(elem)
        return context, self.length

    assert (0)


FormatField.toET = FormatField_toET
FormatField.fromET = FormatField_fromET


def Enum_toET(self, context, name=None, parent=None, is_root=False):
    # FIXME: only works for FormatFields
    return self.subcon.toET(context, name=name, parent=parent)


def Enum_fromET(self, context, parent, name, offset=0, is_root=False):
    # FIXME: only works for FormatFields
    elem = parent.attrib[name]

    mapping = self.encmapping.get(elem, None)

    if mapping is None:
        return self.subcon.fromET(parent=parent, offset=offset, name=name)
    else:
        context[name] = elem
        return context, self.subcon.length


Enum.toET = Enum_toET
Enum.fromET = Enum_fromET


def Bytes_toET(self, context, name=None, parent=None, is_root=False):
    if name is None:
        assert (0)
    if parent is None:
        parent = ET.Element(name)

    assert (isinstance(context[name], bytes))
    parent.attrib[name] = context[name].hex()
    if parent is None:
        return parent
    return None


def Bytes_fromET(self, context, parent, name, offset=0, is_root=False):
    elem = parent.attrib[name]
    b = b"".fromhex(elem)
    return b, len(b), {}


Bytes.toET = Bytes_toET
Bytes.fromET = Bytes_fromET


def GreedyBytes_toET(context, name=None, parent=None, is_root=False):
    if name is None:
        assert (0)
    if parent is None:
        parent = ET.Element(name)

    assert (isinstance(context[name], bytes))
    parent.attrib[name] = context[name].hex()
    if parent is None:
        return parent
    return None


def GreedyBytes_fromET(context, parent, name, offset=0, is_root=False):
    elem = parent.attrib[name]
    b = b"".fromhex(elem)
    context[name] = b
    return context, len(b)


GreedyBytes.toET = GreedyBytes_toET
GreedyBytes.fromET = GreedyBytes_fromET


def StringEncoded_toET(self, context, name=None, parent=None, is_root=False):
    assert (name is not None)
    data = get_current_field(context, name)
    if parent is None:
        return data

    parent.attrib[name] = data
    return None


def StringEncoded_fromET(self, context, parent, name, offset=0, is_root=False):
    if isinstance(parent, str):
        elem = parent
        assert(0)
    else:
        elem = parent.attrib[name]
    if self.encoding == ["ascii", "utf-8"]:
        size = len(elem)
    elif self.encoding in ["utf-16-le", "utf-16-be", "utf-16"]:
        size = len(elem) * 2
    elif self.encoding in ["utf-32"]:
        size = len(elem) * 4
    else:
        assert (0)

    context[name] = elem
    return context, size


StringEncoded.toET = StringEncoded_toET
StringEncoded.fromET = StringEncoded_fromET


def IfThenElse_toET(self, context, name=None, parent=None, is_root=False):
    assert (context is not None)

    if (self.elsesubcon.__class__.__name__ == "Pass"):
        pass
    elif (self.elsesubcon.__class__.__name__ == "Renamed"):
        assert (self.thensubcon.__class__.__name__ == "Renamed")
        assert (self.thensubcon.name != self.elsesubcon.name)
    elif (self.elsesubcon.__class__.__name__ == "Array"):
        assert (self.elsesubcon.count == 0)
    else:
        assert (0)

    c = evaluate(self.condfunc, context)
    if c:
        return self.thensubcon.toET(context=context, name=name, parent=parent)
    else:
        return self.elsesubcon.toET(context=context, name=name, parent=parent)


def IfThenElse_fromET(self, context, parent, name, offset=0, is_root=False):
    def get_elem(name):
        elem = parent.findall(name)
        if len(elem) == 1:
            elem = elem[0]
        elif len(elem) == 0:
            elem = None
        return elem

    elem = parent.attrib.get(name, None)
    # normal -> ident via name
    if elem is None:
        elem = get_elem(name)
    # ident via renamed
    if elem is None:
        if self.thensubcon.__class__.__name__ == "Renamed":
            elem = get_elem(self.thensubcon.name)
    if elem is None:
        if self.elsesubcon.__class__.__name__ == "Renamed":
            elem = get_elem(self.elsesubcon.name)

    if elem is None:
        if self.thensubcon.__class__.__name__ == "Array":
            elem = get_elem(self.thensubcon.subcon.name)
    if elem is None:
        if self.elsesubcon.__class__.__name__ == "Array":
            elem = get_elem(self.elsesubcon.subcon.name)

    # Pass
    if elem is None:
        return self.elsesubcon.fromET(parent=parent, name=name, offset=offset)

    return self.thensubcon.fromET(parent=parent, name=name, offset=offset)


IfThenElse.toET = IfThenElse_toET
IfThenElse.fromET = IfThenElse_fromET


def Switch_toET(self, context, name=None, parent=None, is_root=False):
    key = evaluate(self.keyfunc, context)
    case = self.cases[key]
    return case.toET(context, name=name, parent=parent)


def Switch_fromET(self, parent, name, offset=0, is_root=False):
    for case_id, case in self.cases.items():
        if parent.tag == case.name:
            elems = [parent]
        else:
            elems = parent.findall(case.name)
        assert (len(elems) in [0, 1])
        if len(elems) == 1:
            elem, size, extra = case.fromET(parent=parent, name=case.name, offset=offset)
            extra = extra | {f"_switchid_{name}": case_id}
            return elem, size, extra
    # not found
    assert (0)


Switch.toET = Switch_toET
Switch.fromET = Switch_fromET


def Ignore_toET(self, context, name=None, parent=None, is_root=False):
    # does not need to be in the XML (will be rebuilt)
    return None


def Ignore_fromET(self, parent, name, offset=0, is_root=False):
    # not required in dict, as it will be rebuilt, but size is required
    return None, self.subcon.length, {}


Rebuild.toET = Ignore_toET
Rebuild.fromET = Ignore_fromET
Const.toET = Ignore_toET
Const.fromET = Ignore_fromET


def IgnoreCls_toET(context, name=None, parent=None, is_root=False):
    # does not need to be in the XML (will be rebuilt)
    return None


def IgnoreCls_fromET(parent, name, offset=0, is_root=False):
    # not required in dict, as it will be rebuilt
    return None, 0, {}


Tell.toET = IgnoreCls_toET
Tell.fromET = IgnoreCls_fromET
Pass.toET = IgnoreCls_toET
Pass.fromET = IgnoreCls_fromET


def Pointer_toET(self, context, name=None, parent=None, is_root=False):
    return self.subcon.toET(context=context, name=name, parent=parent)


def Pointer_fromET(self, parent, name, offset=0, is_root=False):
    elem, size, extra = self.subcon.fromET(parent=parent, name=name, offset=0, is_root=is_root)
    assert (len(extra) == 0)
    return elem, 0, {f"_ptrsize_{name}": size}


Pointer.toET = Pointer_toET
Pointer.fromET = Pointer_fromET


def GenericList_toET(self, context, name=None, parent=None, is_root=False):
    data = get_current_field(context, name)
    assert (isinstance(data, ListContainer))
    assert (name is not None)
    assert (parent is not None)
    i = 0
    lst = []
    for item in data:
        ctx = create_child_context(context, name, list_index=i)
        it = self.subcon.toET(context=ctx, name=name, parent=None)
        assert (it is not None)

        if isinstance(it, str):
            # generate list
            assert (len(lst) == i)
            lst.append(it)
        elif isinstance(it, ET.Element):
            assert (len(lst) == 0)
            parent.append(it)
        else:
            assert (0)

        i += 1

    if len(lst) > 0:
        elem = ET.Element(name)
        output = StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(lst)
        elem.text = output.getvalue().strip()
        parent.append(elem)

    return None


def GenericList_fromET(self, parent, name, offset=0, is_root=False):
    elems = parent.findall(name)
    # probably structs
    if len(elems) == 0:
        assert (self.subcon.name is not None)
        name = self.subcon.name
        elems = parent.findall(name)
        assert (len(elems) != 0)
    elif len(elems) == 1 and isinstance(elems[0], ET.Element):
        pass
    # containing array with all basic elements
    elif len(elems) == 1:
        elem = elems[0]
        ass = 0
        for row in csv.reader([elem.text]):
            elems = row
            assert (ass == 0)
            ass = 1

    size = 0
    ret = []
    idx = 0
    ret_extra = {}
    for x in elems:
        elem, csize, extra = self.subcon.fromET(parent=x, name=name, offset=offset, is_root=True)
        assert (len(extra) == 0)
        ret.append(elem)
        ret_extra[f"_offset_{name}_{idx}"] = offset
        ret_extra[f"_size_{name}_{idx}"] = csize
        size += csize
        ret_extra[f"_cursize_{name}_{idx}"] = size
        offset += csize
        ret_extra[f"_endoffset_{name}_{idx}"] = offset
        idx += 1
    return ret, size, ret_extra


Array.toET = GenericList_toET
Array.fromET = GenericList_fromET

RepeatUntil.toET = GenericList_toET
RepeatUntil.fromET = GenericList_fromET


def LazyBound_toET(self, context, name=None, parent=None, is_root=False):
    sc = self.subconfunc()
    return sc.toET(context=context, name=name, parent=parent)


def LazyBound_fromET(self, parent, name, offset=0, is_root=False):
    sc = self.subconfunc()
    return sc.fromET(parent=parent, name=name, offset=offset, is_root=True)


LazyBound.toET = LazyBound_toET
LazyBound.fromET = LazyBound_fromET

Magic = Const
