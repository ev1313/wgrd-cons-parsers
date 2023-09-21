#!/usr/bin/env python3

from wgrd_cons_parsers.common import *

Matrix3x4 = Struct(
    "row0" / Array(4, Float32l),
    "row1" / Array(4, Float32l),
    "row2" / Array(4, Float32l)
)

# Should be same as (or similar) to nodes / dummies / ...
Skeleton = Struct(

    #Base = f.tell()
    #print("skeleton at %d" % Base)
    #FIXME: assert(f.tell() == skeletonOffset)
    #FIXME: assert(skeletonOffset + skeletonSize == len(data))

    #FIXME: Comments are from older script
    "unkf0" / Int32ul, # unk0
    "boneCount" / Int32ul, # count
    "unkf2" / Int32ul, # matricesOffset
    "unkf3" / Int32ul, # parentsOffset
    "unkf4" / Int32ul, # unk10Offset (order?)
    "unkf5" / Int32ul, # nameOffset
    "unkf6" / Int32ul, # matricesSize
    "unkf7" / Int32ul, # parentsSize
    "unkf8" / Int32ul, # unk10Size (order?)
 

    #FIXME: assert(unkf0 == 1)
    #FIXME: assert(unkf1 == boneCount)
    #FIXME: assert(unkf2 == boneCount * 2 + 2 + 9*4)
    #FIXME: assert(unkf6 == boneCount * 3 * (3 * 4) * 4) # matricesDataSize
    #FIXME: assert(unkf7 == boneAnimationOffsets[0])
    #FIXME: assert(unkf8 == unkf7)

    Probe(),

    "_nameLengths" / Struct("nameLengthsArray" / Array(this._.boneCount, "NameLength" / Struct(
        "length" / Int16ul
    ))),
    "unkZero" / Int16ul,
    #FIXME: assert(unkZero == 0)

  
    #FIXME: assert(f.tell() == Base + unkf2)
    "matrixStacks" / Struct("matrixStacksArray" / Array(3, 
        "MatrixStack" / Struct("MatrixStackArray" / Array(this._._.boneCount, 
            "Matrix" / Matrix3x4
        ))
    )),


    #FIXME: assert(f.tell() == Base + unkf3)
    "parents" / Struct("parentsArray" / Array(this._.boneCount, "Parent" / Struct(
        "boneIndex" / Int32ul
    ))),

    #FIXME: assert(f.tell() == Base + unkf4)
    "order" / Struct("orderArray" / Array(this._.boneCount, "Order" / Struct(
        "boneIndex" / Int32ul
    ))),


    #FIXME: assert(f.tell() == Base + unkf5)
    #print("names:")
    "names" / Struct("namesArray" / Array(this._.boneCount, "Name" / Struct(
        "s" / PaddedString(lambda this: this._._._nameLengths.nameLengthsArray[this._._index].length, 'utf-8')
    ))),

)

#Skeleton = Debugger(Skeleton)


if __name__ == "__main__":
    main = CommonMain(Skeleton, "Skeleton")
    main.main()
