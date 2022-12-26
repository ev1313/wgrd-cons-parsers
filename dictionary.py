import pdb
from io import BytesIO
from cons_xml import *

# sorting algorithm used by the game for filepaths
def dictionarySort(l):
    s = []

    def R(a, b):
        l = []
        for x in range(a[0], b[0] + 1):
            l += [bytes([x])]
        return l

    # Allowed symbols and their suspected precedence
    rank = [b'\\'] + [b'-'] + [b'.'] + R(b'0', b'9') + [b'_'] + [b' '] + R(b'a', b'z') + R(b'A', b'Z')

    # print(rank)
    for x in l:
        c = bytes([x])
        # print(c)
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

    def _parse_dictitem(self, stream, **contextkw):
        return self.subcon.parse_stream(stream, **contextkw)

    # used by FileDictionary
    def _allitems_parsed(self, stream, **contextkw):
        return self.dictitems

    def _parse(self, stream, context, path):
        offset = self.offset(context) if callable(self.offset) else self.offset
        size = self.size(context) if callable(self.size) else self.size
        ending = offset+size

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
        assert (unk0 == 0xA)  # Probably header size
        assert (stream.read(6) == b'\x00' * 6)

        # Start recursion
        self.dictitems = parsePath(stream, [], ending)

        return self._allitems_parsed(stream, **context)

    def _build(self, obj, stream, context, path):
        # Stolen from https://stackoverflow.com/a/11016430
        def createTrie(words):
            root = dict()
            for word in words:
                current_dict = root
                for letter in word:
                    current_dict = current_dict.setdefault(bytes([letter]), {})
                current_dict[b''] = None
            return root

        # FIXME: Shouldn't require the `part` argument anymore as we have `path[-1]`
        def parseTrie(trie, path, part, isLast):
            allData = b''

            path += [part]

            #print("%s Enter %s (%s)" % (" |" * len(path), formatDictionaryPath(path), part))

            # FIXME: Use aligned string writer instead
            _part = part + b'\x00'
            if len(_part) % 2 != 0:
                _part += b'\x00'

            trieNodeCount = len(trie.keys())
            for i, node in enumerate(trie.keys()):
                nodeIsLast = (i == (trieNodeCount - 1))

                if node == b'':
                    #print("%s > Found %s (%s)" % (" |" * len(path), formatDictionaryPath(path), part))

                    # FIXME: encode file

                    # Write a file
                    buffer = BytesIO()
                    write32(buffer, 0)
                    write32(buffer, 0 if isLast else 8 + len(data) + len(_part))
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
                        if nodeTrieNode == b'':
                            break
                        nodePart += nodeTrieNode
                        nodeTrie = nodeTrie[nodeTrieNode]

                    data = parseTrie(nodeTrie, [*path], nodePart, nodeIsLast)
                    allData += data

            #print("%s Leave %s (%s)" % (" |" * len(path), formatDictionaryPath(path), part))

            # Write a part
            buffer = BytesIO()
            write32(buffer, 8 + len(_part))
            write32(buffer, 0 if isLast else 8 + len(allData) + len(_part))
            buffer.write(_part)
            buffer.write(allData)

            return bytes(buffer.getbuffer())

        # Get paths
        filePaths = list(self.files.keys())

        # If we don't have any files, we are done; no header will be written
        if len(filePaths) == 0:
            return b''

        # The game expects a specific order
        sortedFilePaths = sorted(filePaths, key=dictionarySort)

        # Create a trie while preserving order
        root = createTrie(sortedFilePaths)

        # Probably header size and 2 fields
        header = b'\x0A\x00\x00\x00' + b'\x00' * 6

        # Note that this also removes some junk from the head
        # FIXME: Ignore b'' in root?
        return header + parseTrie(root, [], b'', True)[10:]

    def _sizeof(self, context, path):
        raise SizeofError(f"Dictionary doesn't support sizeof {path}")


class FileDictionary(Dictionary):
    def __init__(self, subcon, offset, size, offset_data, size_data, sector_size):
        super().__init__(subcon, offset, size)
        self.offset_data = offset_data
        self.size_data = size_data
        self.sector_size = sector_size
        self.files = {}

    def _allitems_parsed(self, stream, **contextkw):
        ctx = Container(**contextkw)
        offset_data = self.offset_data(ctx) if callable(self.offset_data) else self.offset_data
        size_data = self.size_data(ctx) if callable(self.size_data) else self.size_data
        sector_size = self.sector_size(ctx) if callable(self.sector_size) else self.sector_size
        self.files = {}
        for path, header in self.dictitems.items():
            file = Pointer(offset_data + header.offset, Aligned(sector_size, Bytes(header.size))).parse_stream(stream)
            assert(not path in self.files.keys())
            self.files[path] = file

        # FIXME: assert *aligned*
        #assert(size_data == sum([len(f) for _, f in self.files.items()]))

        return self.files
