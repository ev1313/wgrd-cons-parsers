import pdb
from io import BytesIO

import xml.etree.ElementTree as ET

from conshex import *
from conshex.string import *
from conshex.helpers import *

import os
import hashlib


def ctx_get_opt(context, key, default = None):
    ret = None
    if "_root" in context.keys():
        ret = context["_root"].get(key, None)
    if ret is None:
        ret = context.get(key, None)
    return ret if ret is not None else default


# sorting algorithm used by the game for filepaths
def dictionarySort(l):
    s = []
    def R(a, b):
        l = []
        for c in range(ord(a[0]), ord(b[0]) + 1):
            l += [chr(c)]
        return l

    # Allowed symbols and their suspected precedence
    rank = ['\\'] + ['-'] + ['.'] + R('0', '9') + ['_'] + [' '] + R('a', 'z') + R('A', 'Z')

    # print(rank)
    for c in l:
        assert (c in rank)
        s += [rank.index(c)]
    return s


def formatDictionaryPath(path):
    return ",".join([part for part in path])


class Dictionary(Construct):
    def __init__(self, subcon, offset, size):
        super().__init__()
        self.subcon = subcon
        self.offset = offset
        self.size = size
        self.dictitems = {}
        self._dictionary_size = 0

    # parses the dictitem, overloaded by FileDictionary
    def _parse_dictitem(self, stream, **contextkw):
        return self.subcon.parse_stream(stream, **contextkw)

    def _build_dictitem(self, obj, stream, **contextkw):
        path, real_obj = obj
        return self.subcon.build(real_obj)

    # called after all items were parsed to return the final dict
    # overloaded by FileDictionary
    def _allitems_parsed(self, stream, **contextkw):
        return self.dictitems

    def _allitems_build(self, obj, stream, **contextkw):
        return obj

    def _parse(self, stream, context, path):
        offset = self.offset(context) if callable(self.offset) else self.offset
        size = self.size(context) if callable(self.size) else self.size
        ending = offset + size

        if size == 0:
            return {}

        def parsePath(f, path, ending):
            files = {}
            # FIXME: Use count instead?
            while f.tell() != ending:
                c = f.tell()

                pathSize = Int32ul.parse_stream(f)
                entrySize = Int32ul.parse_stream(f)

                # I don't think this should ever be true
                assert ((c + entrySize) != ending)

                # Handle extensions
                if pathSize != 0:

                    s = Aligned(2, CString("utf-8")).parse_stream(f)
                    # print(c, "Y", size, unk1, s)

                    assert (f.tell() == (c + pathSize))

                    #print("DICTIONARY-directory %5d %5d%s %s" % (pathSize, entrySize, "  |" * len(path), formatDictionaryPath(path + [s])))

                    files |= parsePath(f, path + [s], (c + entrySize) if entrySize != 0 else ending)
                else:
                    file = self._parse_dictitem(stream, **context)

                    s = Aligned(2, CString("utf-8")).parse_stream(f)

                    filePath = "".join(path + [s])
                    files[filePath] = file

                    #print("DICTIONARY-file      %5d %5d%s %s" % (pathSize, entrySize, "  |" * len(path), formatDictionaryPath(path + [s])))

                # We should be at the end of this entry now
                assert (f.tell() == ((c + entrySize) if entrySize != 0 else ending))

            # print("Leaving %s" % path)
            return files

        # Read header
        unk0 = Int32ul.parse_stream(stream)
        assert (unk0 in [0x01, 0xA])
        assert (stream.read(6) == b'\x00' * 6)

        # empty dict
        if unk0 == 0x01:
            return {}

        # Start recursion
        self.dictitems = parsePath(stream, [], ending)

        parse_files = ctx_get_opt(context, "_cons_xml_filesdictionary_parse_files", True)
        if parse_files:
            return self._allitems_parsed(stream, **context)
        else:
            return self.dictitems

    def _build(self, obj, stream, context, path):
        if obj is None:
            obj = {}

        # Stolen from https://stackoverflow.com/a/11016430
        def createTrie(words):
            root = dict()
            for word in words:
                current_dict = root
                for letter in word:
                    current_dict = current_dict.setdefault(letter, {})
                current_dict[''] = None
            return root

        # FIXME: Shouldn't require the `part` argument anymore as we have `path[-1]`
        def parseTrie(trie, path, part, isLast):
            allData = b''

            path += [part]

            # print("%s Enter %s (%s)" % (" |" * len(path), formatDictionaryPath(path), part))

            # FIXME: Use aligned string writer instead
            _part = part.encode("utf-8") + b'\x00'
            if len(_part) % 2 != 0:
                _part += b'\x00'

            assert(_part == Aligned(2, CString("utf-8")).build(part))

            trieNodeCount = len(trie.keys())
            for i, node in enumerate(trie.keys()):
                nodeIsLast = (i == (trieNodeCount - 1))

                if node == '':
                    # print("%s > Found %s (%s)" % (" |" * len(path), formatDictionaryPath(path), part))

                    triePath = "".join(path)
                    item = obj[triePath]
                    data = self._build_dictitem((triePath, item), stream, **context)

                    # Write a file
                    buffer = BytesIO()
                    buffer.write(Const(0, Int32ul).build(None))
                    buffer.write(Const(0 if isLast else 8 + len(data) + len(_part), Int32ul).build(None))
                    buffer.write(data)
                    buffer.write(_part)

                    # Ensure that we can leave now
                    # FIXME: Should this not be possible, we might have a file like ["foobar.txt", "foobar.txt.zip"]
                    assert (trieNodeCount == 1)
                    return bytes(buffer.getbuffer())

                else:
                    # Reduce common prefix (like a radix tree)
                    nodePart = node
                    nodeTrie = trie[node]
                    while len(list(nodeTrie.keys())) == 1:
                        nodeTrieNode = list(nodeTrie.keys())[0]
                        if nodeTrieNode == '':
                            break
                        nodePart += nodeTrieNode
                        nodeTrie = nodeTrie[nodeTrieNode]

                    data = parseTrie(nodeTrie, [*path], nodePart, nodeIsLast)
                    allData += data

            # print("%s Leave %s (%s)" % (" |" * len(path), formatDictionaryPath(path), part))

            # Write a part
            buffer = BytesIO()
            buffer.write(Int32ul.build(8+len(_part)))
            buffer.write(Int32ul.build(0 if isLast else 8 + len(allData) + len(_part)))
            buffer.write(_part)
            buffer.write(allData)

            return bytes(buffer.getbuffer())

        filePaths = list(obj.keys())

        # If we don't have any files, we are done; no header will be written
        if len(filePaths) == 0:
            return {}

        # The game expects a specific order
        sortedFilePaths = sorted(filePaths, key=dictionarySort)

        sorted_obj = {}
        for path in sortedFilePaths:
            sorted_obj[path] = obj[path]

        # Create a trie while preserving order
        root = createTrie(sortedFilePaths)

        # Probably header size and 2 fields
        header = b'\x0A\x00\x00\x00' + b'\x00' * 6

        # Note that this also removes some junk from the head
        # FIXME: Ignore b'' in root?
        data = header + parseTrie(root, [], '', True)[10:]
        stream.write(data)
        self._dictionary_size = len(data)

        self._allitems_build(sorted_obj, stream, **context)

        # FIXME: maybe just return correctly sorted dictionary
        return sorted_obj

    def _sizeof(self, obj, context, path):
        raise SizeofError(f"Dictionary doesn't support sizeof {path}")

    def _toET(self, parent, name, context, path):
        assert (name is not None)
        assert (parent is not None)

        files = get_current_field(context, name)
        for dpath, file in files.items():
            elem = self.subcon.toET(obj=file, name=name)
            elem.attrib["path"] = dpath
            assert(elem is not None)
            parent.append(elem)

        return None

    def _fromET(self, parent, name, context, path, is_root=False):
        if isinstance(self.subcon, Renamed):
            elems = parent.findall(self.subcon.name)
        else:
            elems = parent.findall(name)

        ret = context
        ret["_ignore_root"] = True
        ret[name] = {}
        ret[f"{name}_list"] = []
        for elem in elems:
            path = elem.attrib.pop("path")
            ret, child_size = self.subcon.fromET(context=ret, parent=elem, name=f"{name}_list", offset=offset, is_root=True)
            ret[name][path] = Container(ret[f"{name}_list"][0])
            ret[f"{name}_list"] = []

        ret.pop(f"{name}_list")
        ret.pop("_ignore_root")
        # remove _, because conshex rebuild will fail otherwise
        if "_" in ret.keys():
            ret.pop("_")

        # build dictionary to get size of it
        data = self.build(ret[name], **ret)
        ret[f"_{name}_dictionary_offset"] = offset
        ret[f"_{name}_dictionary_size"] = self._dictionary_size
        ret[f"_{name}_dictionary_checksum"] = hashlib.md5(data[0:self._dictionary_size]).digest()

        return ret


class FileDictionary(Dictionary):
    def __init__(self, subcon, offset, size, offset_data, size_data, sector_size):
        super().__init__(subcon, offset, size)
        self.offset_data = offset_data
        self.size_data = size_data
        self.sector_size = sector_size
        self.files = {}
        self._current_offset = 0
        self._data_size = 0

    def _build_dictitem(self, obj, stream, **contextkw):
        ctx = Container(**contextkw)
        path, data = obj
        sector_size = self.sector_size(ctx) if callable(self.sector_size) else self.sector_size
        # only for calculating the correct offsets
        aligned_size = len(data) if len(data) % sector_size == 0 else (int(len(data) / sector_size) + 1) * sector_size
        #print(f"offset {self._current_offset}")
        #print(f"size {len(data)}")
        #print(f"aligned size {aligned_size}")
        ctx = {"offset": self._current_offset,
               "size": len(data),
               "checksum": hashlib.md5(data).digest()}
        self._current_offset += aligned_size
        return self.subcon.build(ctx)

    def _allitems_parsed(self, stream, **contextkw):
        ctx = Container(**contextkw)
        enforce_alignment = ctx_get_opt(ctx, "_cons_xml_filesdictionary_alignment", True)
        disable_checks = ctx_get_opt(ctx, "_cons_xml_filesdictionary_disable_checks", False)

        offset_data = self.offset_data(ctx) if callable(self.offset_data) else self.offset_data
        size_data = self.size_data(ctx) if callable(self.size_data) else self.size_data
        sector_size = self.sector_size(ctx) if callable(self.sector_size) else self.sector_size
        self.files = {}
        for path, header in self.dictitems.items():

            if enforce_alignment:
                file = Pointer(offset_data + header.offset, Aligned(sector_size, Bytes(header.size))).parse_stream(stream)
            else:
                file = Pointer(offset_data + header.offset, Bytes(header.size)).parse_stream(stream)
            assert(not path in self.files.keys())
            self.files[path] = file
            #print(path)
            #print(header.offset)
            #print(header.size)
            #print(header.checksum)
            #print(hashlib.md5(file).digest())
            #print(file[0:40])

            # WARNO has some files (ZZ_2.dat) which have apparently broken checksums
            # FIXME: investigate further
            if not disable_checks:
                assert(header.checksum == hashlib.md5(file).digest())

        # FIXME: assert *aligned*
        #assert(size_data == sum([len(f) for _, f in self.files.items()]))

        return self.files

    def _allitems_build(self, obj, stream, **contextkw):
        ctx = Container(**contextkw)
        sector_size = self.sector_size(ctx) if callable(self.sector_size) else self.sector_size

        # the offset of the files section is also sector_size aligned
        initial_offset = stream.tell()
        aligned_offset = initial_offset if initial_offset % sector_size == 0 else (int(initial_offset / sector_size) + 1) * sector_size
        alignment_size = aligned_offset - initial_offset
        stream.write(b"\x00" * alignment_size)

        size = 0
        for path, data in obj.items():
            aligned_data = Aligned(sector_size, Bytes(len(data))).build(data)
            stream.write(aligned_data)
            #print(data[0:100])
            #print(path)
            #print(f"length {len(data)}")
            #print(f"aligned length {len(aligned_data)}")
            #print(f"rebuild size {size}")
            size += len(aligned_data)
        self._data_size = size

    def _build(self, obj, stream, context, path):
        self._current_offset=0
        super()._build(obj, stream, context, path)

    def _preprocess_size(self, obj: Container, context: Container, path: str, offset: int=0):
        sector_size = self.sector_size(context) if callable(self.sector_size) else self.sector_size

        # build dictionary to get size of it
        data = self.build(obj, **context)

        # calculate data offset
        initial_offset = offset + self._dictionary_size
        aligned_offset = initial_offset if initial_offset % sector_size == 0 else (int(initial_offset / sector_size) + 1) * sector_size
        # set offsets amd sizes
        return obj, {"_dictionary_offset": offset,
         "_dictionary_size": self._dictionary_size,
         "_dictionary_checksum": hashlib.md5(data[0:self._dictionary_size]).digest(),
         "_offset": aligned_offset,
         "_size": self._data_size}

    def _toET(self, parent, name, context, path):
        assert(name is not None)
        assert(parent is not None)
        outpath = ctx_get_opt(context, "_cons_xml_output_directory", None)

        files = context[name]
        for path, file in files.items():
            fspath = os.path.join(outpath, path.replace("\\", os.sep).replace("\\\\", os.sep))
            os.makedirs(os.path.dirname(fspath), exist_ok=True)
            with open(fspath, "wb") as f:
                f.write(file)
                child = ET.Element("File")
                child.attrib["path"] = path
                parent.append(child)

        return None

    def _fromET(self, parent, name, context, path, is_root=False):
        elems = parent.findall("File")
        context[name] = {}
        for elem in elems:
            inpath = ctx_get_opt(context, "_cons_xml_input_directory", ".")

            path = elem.attrib["path"]
            filepath = os.path.join(inpath, path.replace("\\", os.sep).replace("\\\\", os.sep))
            data = open(filepath, "rb").read()
            context[name][path] = data

        return context