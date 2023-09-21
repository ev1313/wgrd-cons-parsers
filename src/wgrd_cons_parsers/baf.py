#!/usr/bin/env python3

from wgrd_cons_parsers.common import *

from wgrd_cons_parsers.skeleton import Skeleton

Baf = Struct(
    "unk0" / Int32ul,
    #FIXME: assert(unk0 == 0xF)
    "duration" / Float32l, # Probably duration in seconds
    "frameCount" / Int16ul, # Probably played at 30 Hz
    "boneCount" / Int16ul,
    "boneAnimationDataOffset" / Int32ul,
    "skeletonOffset" / Int32ul,
    "boneAnimationDataSize" / Int32ul,
    "skeletonSize" / Int32ul,

    #FIXME: assert(boneAnimationDataOffset + boneAnimationDataSize == skeletonOffset)
    #FIXME: assert(f.tell() == boneAnimationDataOffset)

    # Pointers into unkX
    "_boneAnimationOffsets" / Struct("boneAnimationOffsetsArray" / Array(this._.boneCount, "BoneAnimationOffset" / Struct(
        "offset" / Int32ul,
    ))),


    "boneAnimations" / Struct("boneAnimationsArray" / Array(this._.boneCount, "BoneAnimation" / Struct(
        #FIXME: assert(f.tell() == (boneAnimationDataOffset + boneAnimationOffsets[j]))

        "positionsCount" / Int32ul,
        "scalesCount" / Int32ul,
        "thingsCount" / Int32ul,
        #FIXME: assert(scalesCount == 1)


        "positions" / Array(this.positionsCount, Struct(
            "t" / Int32ul,
            "x" / Float32l,
            "y" / Float32l,
            "z" / Float32l,
            #FIXME: assert(t <= 0x7FFFFF)
        )),
        "scales" / Array(this.scalesCount, Struct(
            "t" / Int32ul,
            #FIXME: assert(t == 0)
            "x" / Float32l,
            "y" / Float32l,
            "z" / Float32l,
            #FIXME: assert(t <= 0x7FFFFF)
        )),
        "things" / Array(this.thingsCount, Struct(
            "t" / Int32ul,
            "unke1" / Int16sl,
            "unke2" / Bytes(6),
            #FIXME: assert(t <= 0x7FFFFF)
        ))
    ))),

    #FIXME: assert(f.tell() == skeletonOffset)
    "skeleton" / Skeleton,


    #FIXME:
    #readPad(f, f.tell(), 4)
    "rest" / Struct("data" / GreedyBytes),

    #assert(f.tell() == len(data))
)





#Baf = Debugger(Baf)

if __name__ == "__main__":
    main = CommonMain(Baf, "Baf")
    main.main()
