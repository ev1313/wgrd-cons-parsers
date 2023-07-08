#!/usr/bin/env python3

from .common import *

# Fine tuned for _2x2_port_Wonsan_v11.dat => /output/highdef.tms of 

Ibuf = Struct(
    "IbufRange" / GreedyRange("Face" / Struct(
        "a" / Int16ul,
        "b" / Int16ul,
        "c" / Int16ul,
    ))
)

UnkStruct = Struct(
    "x0Offset" / Int16ul,
    "x1Count" / Int16ul, # Some count for x1?
    "x2Offset" / Int16ul,
    "x3Count" / Int16ul, # some count for x2?
    "x4Offset" / Int16ul,
    "x5Count" / Int16ul, # some count for x4?
    "x6" / Int16ul,
    "x7" / Int16ul,
    "x8" / Int16ul,
    "x9" / Int16ul
)

TmsChildHead = Struct(
    "unk0" / Int32ul,
    "unk1" / Int32ul, # vbuf data offset
    "unk2" / Int32ul,
    "unk3" / Int32ul,
    "unk4" / Int32ul,
    "unk5" / Int32ul,
    "unk6" / Int32ul,
    "unk7" / Int32ul,
    "unk8" / Int32ul,
    #FIXME: assert(unk0 == 3)

    "vertexFormat" / PaddedString(512, 'utf-8'),
)

# This is where we expect the child_head.bin and child_data.bin split
TmsChildData = Struct(
    #FIXME: Base = f.tell()

    #print(hex(unk1 // 3))
    #print(hex(unk2-unk1))

    #print(Base + unk1)
    #print(Base + unk1 + unk2)

    # Surface
    "draw0_ibuf" / FixedSized(this._.childHead.unk1, "draw0_ibuf" / Ibuf), #dump(f, "tms_child/draw0_ibuf.bin", Base + 0, unk1)
    "draw0_vbuf" / Bytes(this._.childHead.unk2), #dump(f, "tms_child/draw0_vbuf.bin", Base + unk1, unk2)
    "draw0_unk0" / Bytes(this._.childHead.unk3), #dump(f, "tms_child/draw0_unk0.bin", Base + unk1 + unk2, unk3) # Some floats; bbox?
    "draw0_unk1" / Bytes(this._.childHead.unk4), #dump(f, "tms_child/draw0_unk1.bin", Base + unk1 + unk2 + unk3, unk4) # Some offsets?

    # Water
    "draw1_ibuf" / FixedSized(this._.childHead.unk5, "draw1_ibuf" / Ibuf), #dump(f, "tms_child/draw1_ibuf.bin", Base + unk1 + unk2 + unk3 + unk4, unk5) # some ibuf
    "draw1_vbuf" / Bytes(this._.childHead.unk6), #dump(f, "tms_child/draw1_vbuf.bin", Base + unk1 + unk2 + unk3 + unk4 + unk5, unk6) # some vbuf
    "draw1_unk0" / Bytes(this._.childHead.unk7), #dump(f, "tms_child/draw1_unk0.bin", Base + unk1 + unk2 + unk3 + unk4 + unk5 + unk6, unk7) # some floats: bbox?
    "draw1_unk1" / Bytes(this._.childHead.unk8), #dump(f, "tms_child/draw1_unk1.bin", Base + unk1 + unk2 + unk3 + unk4 + unk5 + unk6 + unk7, unk8) # some offsets?

    #print(len(data) - (Base + unk1 + unk2 + unk3 + unk4 + unk5 + unk6 + unk7 + unk8))

    #f.seek(Base + unk1 + unk2 + unk3 + unk4 + unk5 + unk6 + unk7 + unk8)

    #"x" / Const(b'TMSG')

    #FIXME: assert(f.tell() == len(data))
)

TMSG = Struct(
    "magic" / Const(b"TMSG"),
    "unkX" / Int32ul,
    "platform" / Const(b'PC\x00\x00'),
    "unk0" / Int32ul,
    #FIXME: assert(unk0 == len(data))
    "unk1_xtiles" / Int32ul, # xtiles
    "unk2_ytiles" / Int32ul, # ytiles
    "unk3" / Int32ul, # ???
    #FIXME: assert(unk3 in [4, 8])
    "unk4" / Int32ul,
    "unk5" / Int32ul,
    #FIXME: assert(unk5 == unk4)
    
    "unk6Offset" / Int32ul, # offset
    "unk7Size" / Int32ul, # size
    
    "unk8Offset" / Int32ul, # offset
    "unk9Size" / Int32ul, # size
    #FIXME: assert(unk8 == unk6 + unk7)

    "unk10Offset" / Int32ul, # data offset
    "unk11Size" / Int32ul, # data size
    #FIXME: assert(unk10 == unk8 + unk9)

    "vertexFormat" / PaddedString(526-2, 'utf-8'), #FIXME: String
    
    "a0_sizeX" / Float32l,
    "a1_sizeY" / Float32l,
    "a2" / Int32ul,
    "a3" / Int32ul,
    "a4" / Int32ul,
    "a5" / Int32ul,
    "a6" / Int32ul,
    
    #FIXME: assert(a3 == unk10 + unk11)
    #FIXME: assert(a5 == a3 + a4)

    "pad0_offset" / Tell,
    "pad0" / Bytes(this.unk6Offset - this.pad0_offset),
    #FIXME: assert(pad == b'\x00' * len(pad))

    #FIXME: assert(f.tell() == unk6Offset)

    # Data offsets
    "dataOffsets" / Struct("dataOffsetsArray" / Array(this._.unk1_xtiles * this._.unk2_ytiles, "DataOffset" / Struct(

        "x0" / Int32ul, # data type: 0x3=VBUF, 0x7=???
        "x1" / Int32ul, # data vbuf offset
        "x2" / Int32ul, # data vbuf size
        "x3" / Int32ul, # vbuf count?
        "x4" / Int32ul, # data ibuf offset [follows vbuf]
        "x5" / Int32ul, # data ibuf size?
        "x6" / Int32ul, # ibuf count?
        "x7" / Int32ul, # some offset? [follows ibuf]
        "x8" / Int32ul, # some size?
        "x9" / Int32ul, # some count?
        "xOffset" / Int32ul, # Byte offset in c1container
        "xSize" / Int32ul, # Byte size in c1container
        
        #FIXME: assert(x0 in [0x1, 0x3, 0x5, 0x7])
        #FIXME: assert(x1 % 4 == 0)
        #FIXME: assert(xSize in [0x140, 0x200, 0x500, 0x800])

        #dump(f, "tms/data_vbuf%d_%d.bin" % (i, x3), unk10 + x1, x2)
        #dump(f, "tms/data_ibuf%d_%d.bin" % (i, x6), unk10 + x4, x5)
        #dump(f, "tms/data_unk%d_%d.bin" % (i, x9), unk10 + x7, x8)
    ))),

    #FIXME: Use dataOffsets from above
    "c1container" / Struct("c1containerArray" / Array(this._.unk1_xtiles * this._.unk3, 
        "c1" / Struct("c1Array" / Array(16, "c1ArrayStruct" / UnkStruct)),
    )),
    

    "cX_offset" / Tell, # f.tell() < unk10: 
    #"cX" / FixedSized(this.unk10Offset - this.cX_offset, GreedyRange(Struct("c1Array" / Array(16, "c1ArrayStruct" / UnkStruct)))),
    "cX" / Struct("cXdata" / Bytes(this._.unk10Offset - this._.cX_offset)),
    Probe(),


    # Skip vbuf
    #FIXME: assert(f.tell() == unk10)
    "vbufs" / Bytes(this.unk11Size),
    #assert(buffer[0:4] == b'VBUF')
    #vbufi = -4
    #while vbufi != -1:
    #    vbufi = buffer.find(b"VBUF", vbufi + 4)
    #    print("VBUF at ", vbufi, hex(vbufi))
    ##FIXME: Dump!
    #dumpBytes("tms/data.bin", buffer)

    #FIXME: assert(f.tell() == a3)

    #FIXME: Another tmsg file starts here again?!

    #"pad1" / Bytes(a4),
    #if a6 == 0:
    #    assert(pad == b'\x00' * len(pad))
    #dumpBytes("tms/child_head.bin", pad)

    #FIXME: assert(f.tell() == a5)
    #if (a6 != 0):
    #    "unkChild" / Bytes(a6)
    #    dumpBytes("tms/child_data.bin", unkChild)
    
    #Probe(),

    #dump(f, "tms/child.bin", a3, a5+a6)
    "childHead" / FixedSized(this.a4, TmsChildHead),
    "childData" / FixedSized(this.a6, TmsChildData),


    "footerMagic" / Const(b'TMSG'),

    #FIXME: assert(f.tell() == len(data))
    #Probe(),
)

#TMSG = Debugger(TMSG)

if __name__ == "__main__":
    main = CommonMain(TMSG, "TMSG")
    main.main()
