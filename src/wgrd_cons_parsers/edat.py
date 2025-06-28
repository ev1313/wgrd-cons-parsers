#!/usr/bin/env python3

from wgrd_cons_parsers.dictionary import *

from conshex import Struct, Int32ul, Padding, Bytes, Rebuild, this, Const, Magic

from wgrd_cons_parsers.common import CommonMain

EDatFileHeader = Struct(
    "offset" / Int32ul,
    "pad0" / Padding(4),
    "size" / Int32ul,
    "pad" / Padding(4),
    "checksum" / Bytes(16), # md5 checksum of the file itself
)

EDat = Struct(
    "magic" / Magic(b"edat"),
    "unk0" / Const(2, Int32ul), # number of tables maybe?
    "pad0" / Padding(17),
    "offset_files" / Rebuild(Int32ul, this._files_meta._dictionary_offset),
    "size_files" / Rebuild(Int32ul, this._files_meta._dictionary_size),
    "offset_data" / Rebuild(Int32ul, this._files_meta._offset),
    "size_data" / Rebuild(Int32ul, this._files_meta._size),
    "pad1" / Padding(4),
    "sectorSize" / Int32ul,
    "checksum" / Rebuild(Bytes(16), this._files_meta._dictionary_checksum), # md5 checksum of the whole files section
    "pad2" / Padding(972),
    "files" / FileDictionary(EDatFileHeader, this.offset_files, this.size_files, this.offset_data, this.size_data, this.sectorSize),
    #"data" /
)

class EdatMain(CommonMain):
    def __init__(self):
        super().__init__(EDat, "EDat")

    def parse(self, args=None):
        self.parser.add_argument("-c", "--no-alignment", action="store_true",
                            help="don't check for correct alignment when reading files (just use the offsets)")
        self.parser.add_argument("-d", "--disable-checksums", action="store_true",
                            help="don't check for correct checksums of the files")
        super().parse(args)

    def add_extra_args(self, input_path, output_path, ctx={}):
        ctx = ctx | {"_cons_xml_filesdictionary_alignment": not self.args.no_alignment,
                     "_cons_xml_filesdictionary_disable_checks": self.args.disable_checksums}
        return super().add_extra_args(input_path=input_path, output_path=output_path, ctx=ctx)


if __name__ == "__main__":
    main = EdatMain()
    main.main()
