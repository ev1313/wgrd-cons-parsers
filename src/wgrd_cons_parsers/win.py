#!/usr/bin/env python3

from wgrd_cons_parsers.common import *

BBOX = Struct(
    "a1" / Int32ul, # Probably float!
    "b1" / Int32ul, # Probably float!
    "c" / Float32l,
    "d" / Float32l,
    #FIXME: assert(a1 == 0)
    #FIXME: assert(b1 == 0)
)

R0AD = Struct(

    "count" / Int16ul,
    "unk0" / Int16ul,
    "unk1" / Int32ul,
    "unk2" / Int32ul,
    "unk3" / Int32ul,
    "unk4" / Int32ul,

    #FIXME: assert(fi.tell() == unk1)

    # Vertices?
    "vertices" / Struct( #FIXME: Hacky array due to cons_xml issues
        "verticesArray" / Array(this._.count, "Vertex" / Struct(
            "unka" / Int8ul, # Count
            "unkb" / Int16ul, # Offset
            "unkc" / Int8ul, # always 0
            "x" / Float32l, # Road center X
            "y" / Float32l, # Road center Y
            #FIXME: assert(unkc == 0)
        )),
    ),
    #FIXME: assert(fi.tell() == unk2)

    # Edges
    "edges" / Struct( #FIXME: Hacky array due to cons_xml issues
        "edgesArray" / Array(this._.unk0, "Edge" / Struct(
            "vertexIndexA" / Int16ul,
            "vertexIndexB" / Int16ul,
            "edgeLength" / Int16ul, # Distance / 10 (?)
        )),
    ),

    #FIXME: assert(fi.tell() == unk3)

    # Line indices?
    "unkArray2" / Struct( #FIXME: Hacky array due to cons_xml issues
        "unkArray2Array" / Array(this._.unk0, "unkArray2Element" / Struct(
            "ia" / Int16ul,
            "ib" / Int16ul,
            #"s" / Bytes(4)
        )),
    ),

    # assert(fi.tell() == unk4)

    # ???
    "unkGreedyRangeContainer" / Struct( #FIXME: Hacky array due to cons_xml issues
        "unkGreedyRange" / GreedyRange(Struct(
            #L = fi.tell() - unk4
            "h" / Int16ul,
            #print("    [%d] @%d h=0x%04X" % (i, L, h), end="")
            "data" / Switch(this.h, {
                0x1: Struct(
                    "s" / Bytes(2),
                    "x" / Float32l,
                ),
                0x6: Struct(
                    "s" / Bytes(6)
                ),
                0x8: Struct(
                    "s0" / Int16ul,
                    "s1" / Int16ul,
                    "s2" / Int16ul,
                    "s3" / Int16ul,
                    "s4" / Int16ul,
                    #FIXME: assert(s4 == 0)
                ),
                0xA: Struct(
                    "s" / Bytes(10)
                ),
                0xC: Struct(
                    "s" / Bytes(7 * 2)
                    # s=1502 1a07 f006 d302 f106 f206 0000 0c00 1502 1a07 1b07 d302 d102 e202 0000 0100 2500 afc84248
                    # #0100 1100 b83c7049010007000e071f480800e702e802ea02e90200000a00e702e402e602e302e50201000700b291d5470800ee02f102f002ef0200000a00
                ),
                0xE: Struct(
                    "s" / Bytes(7 * 2)
                    # s=a702 1607 ea01 1507 bc06 c401 bd06 0e00 a702 1607 e901 1507 9d02 c401 9c02
                    # s=fb01 0102 0002 ff01 fe01 fc01 fd01 0100 0700 9c73 0849 0a00 3902 3a02 3802 3b02 3702 0a00 4702 4802 4a02 4602 3702
                    # 0100 1300 4e6c7e49
                    # 010007003fbc11490a0002020302da01d90101020c00d2010302d801d901d3010402000001000700cfa810490a004a024902de01dd01dc010c00e001db01de01da01dc01df010000010025009826
                    #  0100 1100 d0616c49
                    #  01000700b84be2480800e301e501e401e20100000a00f201f301f401f501f60101000700ed38e64808009c02e1019b02e20100000c00fb01f701fa01f801
                ),



                # This is a hack for _4x4_Marine_5_v11.dat/output/mapinfo.win because there are no roads
                0x0: Struct (
                    "s" / Const(b'\x00\x00')
                ),


            })

            #FIXME: This might be chunked
            # 0x0001 = uint16, float
            # 0x0008 = uint16
            
            # 0100 4d0a 568e1949
            # 0100 0905 ccdb6249
            # 0100 7f02 dbcb6648
            # 0100 3d01 f65ae848
            # 0100 9d00 58f6fb47
            # 0100 4d00 72ac8248
            # 0100 2500 328c9c47
            # 0100 1100 bbaf0c47
            # 0100 0700 66048947
            # 0800 0000 0100 0200 0300 0000 0a00 0400 0700 0600 0300 0500 0100 0700 181b9247
            # 0800 0800 0700 0900 0a00 0000 0a00 0e00 0d00 0c00 0a00 0b00 0100 1100 90b3aa47
            # 0100 0700 22d2a847
            # 0800 0e00 0f00 1000 1100 0000 0a00 1200 1600 1400 1100 1300 0100 0700 5c5bdc47
            # 0800 1500 1600 1700 1800 0000 0a00 1c00 1b00 1700 1a00 1900 0100 2500 53d89947
            # 0100 1100 0a56d348
            # 0100 0700 7a9e6747
            # 0800 fe00 f900fa00fb0000000a00fe0003010201fc00fd0001000700d3729f460a00190115011601170118010a001c011a011601f9001b010100110072f2c948010007009082b6470a00ff0000010601040105010a0009010a0106010801070101000700d04ada470a0001010a01ff000b0102010a000f010e010d010b010c0101004d00a0d35c4801002500cf22194801001100c6621348010007008692054808001c001d001e001f0000000a002000
            # [....]
            # foo = """
            #h=0x0006 s=8f01 8d01 8e01 0a00 2701 2901 2601 2a01 2801
            #0100 0700 ac24d647
            #0a00970191018f01900192010c009601910195019401920193010000010011002e59ff4801000700a4aa404808002d012a012c012b0100000a002d01310130012f012e0101000700d239
            #                   """
        )),
    ),

    #FIXME: assert(fi.tell() == len(d))
)


PATH = Struct(

    # Parse PATH data (starts with GRA3)

    "magic" / Const(b'GRA3'),
    "gra3a" / Int32ul,
    "gra3b" / Int32ul,
    "gra3c" / Int32ul,
    "gra3da" / Int16ul,
    "gra3db" / Int16ul,
    "gra3e" / Int32ul,
    "gra3f" / Int32ul,
    "gra3g" / Int32ul,
    "gra3h" / Int32ul,
    "gra3i" / Int32ul,

    "magic" / Const(b'GRA3'),

    #FIXME: assert(fi.tell() == gra3e - 8)

    "unkArray0" / Struct( #FIXME: Hacky array due to cons_xml issues
        "unkArray0Array" / Array(this._.gra3da, "unkArray0Element" / Struct(
            "xa" / Int32ul,
            "xb" / Int32ul,
            "xca" / Int8ul,
            "xcb" / Int8ul,
            "xcc" / Int8ul,
            "xcd" / Int8ul,
            "px" / Float32l,
            "py" / Float32l, 
            "pz" / Float32l,
        ))
    ),

    
    #FIXME: assert(fi.tell() == gra3f - 8)

    "count" / Int32ul, #FIXME: I believe this is actually a count of elements; but because there's always pairs, this should always be a multiple of 2?
    "unk0" / Int16ul,
    "unkArray1" / Struct( #FIXME: Hacky array due to cons_xml issues
        "unkArray1Array" / Array(this._.count, "unkArray1Element" / Struct(
            "s" / Int16ul,
        )),
    ),

    "countb" / Int16ul,

    #FIXME: assert(fi.tell() == gra3g)


    #FIXME: Incomplete!

    "unkArray2" / Struct( #FIXME: Hacky array due to cons_xml issues
        "unkArray2Alignment" / Aligned(4, "unkArray2Array" / Array(this._.unk0, "unkArray2Element" / Struct(
            "s" / Int16ul,
        ))),
    ),

    #FIXME: assert(fi.tell() == gra3h)

    "s" / Bytes(4),


    # There's clearly some sort of hierarchy or pattern in the data below; it's just not clear how
    #    0100 7f00 f62b41491361f448
    #      0100 3d00 bb1b89490a3c4b49
    #        0100 1700 ed7ed4484c18eb47
    #          0100 0900 ed40e048263e7a48
    #            0c00 7100 7200 6a00 6b00 6000 6100 0000
    #            0e00 5b00 5800 5000 4c00 4800 4700 3f00
    #              0100 0900 f674254913b6b348
    #            0e00 6f00 7000 6900 6600 5d00 5e00 5500
    #              0100 0700 f6bd094913a39448
    #          0800 5600 4100 4b00 3e00 0000
    #          0800 4600 4f00 3d00 4500 0000
    #        0100 1700 ed17e14826620b48
    #          0100 0900 7bd3ca4905a5a949
    #            0e00 3900 3300 3000 2a00 2800 2700 2000
    #            0e00 1a00 1800 1100 0d00 0e00 0800 0700
    #              0100 0900 7b81cc49c57ea649
    #            0e00 3800 3200 2e00 2f00 2500 2600 1e00
    #              0100 0700 768f124913a39448
    #          0800 1700 0600 1f00 0c00 0000
    #          0800 1600 0500 0b00 1500 0000

    #      0100 3d00 3b2b8649ca3d5c49
    #      0100 1700 3b5e8a498ad04a49
    #      0100 0900 76eb1549131da748 0e00 6e00 6d00 6800 6500 5f00 5c00 5700
    #                                 0e00 5400 5300 4e00 4d00 4400 4000 3c00
    #      0100 0900 76a40749133bb648 0e00 6c00 6700 6400 6300 6200 5a00 5900
    #      0100 0700 3b5d9f4945488049 0800 4a00 3b00 4300 5200 0000
    #                                 0800 3a00 4900 5100 4200 0000

    #      0100 1700 7bad8c490a134c49
    #      0100 0900 fb15cc49c555a749 0e00 3700 3600 2d00 2c00 2400 2300 1d00
    #                                 0e00 1c00 1400 1000 0a00 0200 0400 0300
    #      0100 0900 7bbfc049c555a749 0e00 3400 3500 3100 2b00 2900 2100 2200
    #      0100 0700 7bfe9f4945cd8249 0800 1900 0f00 0100 1300 0000
    #                                 0800 0900 1b00 1200 0000 0000
    # ...



    "chunks" / GreedyRange(Struct(
        StopIf(lambda obj, lst, ctx: ctx._io.tell() < 4 + this._.gra3i),
        "unk0" / Int16ul,
        "unk1" / Int16ul,
        "data" / Switch(this.unk0, {
            0x1: Struct (
                "s" / Bytes(8)
            ),
            0x2: Struct (
                "s" / Bytes(0)
            ),
            0x4: Struct (
                "s" / Bytes(4)
            ),
            0x6: Struct (
                "s" / Bytes(4)
            ),
            0x8: Struct (
                "s" / Bytes(8)
            ),
            0xA: Struct (
                "s" / Bytes(8)
            ),
            0xC: Struct (
                "s" / Bytes(12)
            ),
            0xE: Struct (
                "s" / Bytes(12)
            ),
        })
    )),

    "rest" / Struct("data" / GreedyBytes),
    #FIXME: Rest of file!
    #FIXME: assert(fi.tell() == 4 + gra3i)
    #FIXME: assert(fi.tell() == len(d))
)




Win = Struct(
    "magic" / Const(b"INFO"),
    "chunk" / GreedyRange(Struct(
        "chunkMagic" / Bytes(4),
        StopIf(this.chunkMagic == b'INFO'),
        "data" / Switch(this.chunkMagic, {
            b'I0\r\n': "IO" / Struct(
                "a" / Int32ul, # Version? always 1?
                "b" / Int32ul, # Chunkcount
                "c" / Int32ul, # Size

                #FIXME: Should read all children here?

                #FIXME: assert(20 + c == len(data))
            ),
            b'BBOX': "BBOX" / Struct(
                "a" / Int32ul,
                "b" / Int32ul,
                "d" / FixedSized(this.b, BBOX),
                "magic" / Const(b'BBOX')
            ),
            b'R0AD': "R0AD" / Struct(
                "a" / Int32ul,
                "b" / Int32ul,
                "d" / FixedSized(this.b, R0AD),
                #dumpBytes("win/%d_R0AD.bin" % i, d)
                "magic" / Const(b'R0AD')
            ),
            b'PATH': "PATH" / Struct(
                "a" / Int32ul,
                "b" / Int32ul,
                "d" / FixedSized(this.b, PATH),
                #dumpBytes("win/%d_PATH.bin" % i, d)
                "magic" / Const(b'PATH')
            ),
            b'VISI': "VISI" / Struct(
                "a" / Int32ul,
                "b" / Int32ul,
                "x" / Bytes(this.b),
                #dumpBytes("win/visi.sdb", x)
                "magic" / Const(b'VISI')
            ),
            b'TERR': "TERR" / Struct(
                "a" / Int32ul,
                "b" / Int32ul,
                "x" / Bytes(this.b),
                #dumpBytes("win/terr.sdb", x)
                "magic" / Const(b'TERR')
            )
        }),
    )),
    "rest" / Struct("data" / GreedyBytes),
    #FIXME: assert(f.tell() == len(data))
)


#Win = Debugger(Win)

if __name__ == "__main__":
    main = CommonMain(Win, "Win")
    main.main()
