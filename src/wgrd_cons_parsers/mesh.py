#!/usr/bin/env python3

from wgrd_cons_parsers.common import *

Mesh = Struct(
    "magic " / Const(b'ZONE'),
    "unk0" / Int16ul,
    "unk1" / Int32ul,
    "unk2" / Int16ul,
    "unk3" / Int16ul,
    "unk4" / Int16ul,
    "unk5" / Int32ul, # section count?
    "sec1Offset" / Rebuild(Int32ul, this._offset_SEC1), # SEC1 offset
    "sec2Offset" / Rebuild(Int32ul, this._offset_SEC2), # SEC2 offset
    "sec3Offset" / Rebuild(Int32ul, this._offset_SEC3), # SEC3 offset

    #assert(unk0 == 2)
    #assert(unk1 == len(data))
    #assert(unk5 == 3)

    #assert(f.tell() == sec1Offset)
    "SEC1" / Struct(
        "magic" / Const(b'SEC1'),

        "unkA" / Int32ul,
        "unkB" / Int32ul, # Section size?
        #print("SEC1 unkA=0x%X unkB=%d" % (unkA, unkB))

        "unkArray0" / Array(11, "unkArray0Item" / Struct(
            "l" / Rebuild(Int16ul, len_(this.s.value)),
            "u" / Int16ul,
            "s" / Aligned(4, Struct("value" / StringEncoded(Bytes(this._.l), 'utf-8'), "_zero" / Const(b'\x00'))),
            #"z" / Int8ul,
            #assert(z == 0)
            #readPad(f, f.tell(), 4)
        )),
    ),

    # at 180
    #assert(f.tell() == sec2Offset)
    "SEC2" / Struct(
        "magic" / Const(b'SEC2'),

        "unkA" / Int32ul,
        "unkB" / Int32ul, # Section size?

        "vertexCount" / Int32ul,
        "minX" / Float32l,
        "minY" / Float32l,
        "maxX" / Float32l,
        "maxY" / Float32l,
        "vertices" / Array(this.vertexCount, "Vertex" / Struct(
            "x" / Float32l,
            "y" / Float32l
            #print("v %f 0.0 %f # OBJ" % (px, py))
        )),
    ),

    # at 22012
    #assert(f.tell() == sec3Offset)
    "SEC3" / Struct(
        "magic" / Const(b'SEC3'),

        "unkA" / Int32ul,
        "unkB" / Int32ul, # Section size?

        # Read some other table
        "faceCount" / Int32ul,
        "faces" / Array(this.faceCount, "Face" / Struct(
            "vertexIndexA" / Int32ul, # Index into SEC2
            "vertexIndexB" / Int32ul, # Index into SEC2
            "vertexIndexC" / Int32ul, # Index into SEC2
            "sdbMask" / Int32ul # ???
        ))
    )

    #assert(f.tell() == len(data))
)

#Mesh = Debugger(Mesh)


if __name__ == "__main__":
    main = CommonMain(Mesh, "Mesh")
    main.main()
