#!/usr/bin/env python3

from wgrd_cons_parsers.common import *

foo = 0
def StructArray(count, struct):
    global foo
    name = "Foo%d" % foo
    foo += 1
    return Struct(("%s_array" % name) / Array(count, struct))

# WIP on MD5 (out/edat/output/save.boobspc) = fb1889fec7ee8013b58d21ccb074a709
# Probably Maps/WarGame/PC/_2x2_port_Wonsan_v11.dat

isSave = False

String = Struct(
    #L = f.tell()
    "unk0" / Int16ul,
    "length" / Int8ul,
    "s" / Padded(61, StringEncoded(Bytes(this.length), 'utf-8'), b'\xCD')
    #assert(s[length] == 0)
    #assert(s[length+1:] == b'\xCD' * (60 - length))
)

dumpx7 = GreedyRange(Struct(
    #L = f.tell()
    "x0" / Bytes(4),
    "x1" / Int8ul,
    "x2a" / Int8ul,
    "x2b" / Int8ul,
    "x2c" / Int8ul,
    "x2d" / Int8ul,
    "x2e" / Int8ul,
    "x2f" / Int8ul,
    "x2g" / Int8ul,
    "x3a" / Int16ul,
    "x3b" / Int16ul,
    "x4a" / Int16ul,
    "x4b" / Int16ul,
    #FIXME: assert(x2b <= x2a) # Mostly equal
    #FIXME: assert(x2c <= x2a) # Mostly equal
))

T00 = Struct(
    "f0" / Float32l, # x offset
    "f1" / Float32l, # y offset
    "s" / Bytes(4) # Probably also float
)
T01 = T00
T10 = Struct(
    "s" / Bytes(8)
)
T11 = T10
T20 = Struct(
    "s" / Bytes(12)
)
T21 = T20
T30 = Struct(
    "s" / Bytes(16)
)
T31 = T30
T40 = Struct(
    "e0" / Float32l,
    "e1" / Float32l,
    "e2" / Float32l,
    "e3" / Float32l,
    "f0" / Float32l,
    "f1" / Float32l
    #if False:
    #    if gx != None:
    #        print("\ng type_0x%X_0x%X # OBJ" % (x, s1))
    #        print("v %f %f %f # OBJ\n" % (gx+e2, 0.0, gy+e3))
    #
)
T41 = T40
T50 = Struct(
    "s" / Bytes(24)
)
T60 = Struct(
    "e0" / Float32l,
    "e1" / Float32l,
    "e2" / Float32l,
    "e3" / Float32l,
    "f0" / Float32l,
    "f1" / Float32l,
    #if False:
    #    if gx != None:
    #        print("\ng type_0x%X_0x%X # OBJ" % (x, s1))
    #        print("v %f %f %f # OBJ\n" % (gx+e2, 0.0, gy+e3))
)
T61 = T60

T80 = Struct("s" / Bytes(12))
T81 = T80

T82 = Struct("s" / Bytes(60))

T90 = Struct("s" / Bytes(8))
T91 = T90

TA0 = Struct(
    "f0b" / Int16ul,
    "f1" / Int32ul,
    "x" / Int32ul,
    "s" / Bytes(2),
    #s" / Bytes(12)
)
TA1 = TA0

TB0 = Struct(
    "s" / Bytes(16)
)
TB1 = TB0

TC0 = Struct(
    # 24 bytes
    "e0" / Float32l,
    "e1" / Float32l,
    "e2" / Float32l,
    "e3" / Float32l,
    "f0" / Float32l,
    "f1" / Float32l,
    #if True:
    #    if x & 1:
    #        if gx != None:
    #            if (abs(e2) > 327680.000000*2) or (abs(e3) > 327680.000000*2):
    #                print(" WEIRD!")
    #            else:
    #                print(" GOOD!")
    #            print("\ng type_0x%X_0x%X # OBJ" % (x, s1))
    #            print("v %f %f %f # OBJ\n" % (gx+e2, 0.0, gy+e3))
)
TC1 = TC0   

TD0 = Struct("s" / Bytes(24))
TD1 = TD0

TE0 = Struct(
    # 24 bytes
    "e" / Bytes(16),
    "f0" / Float32l,
    "f1" / Float32l
)
TE1 = TE0

TF0 = Struct("s" / Bytes(48))
TF1 = TF0

dumpx9 = GreedyRange(
    Struct( #(d, offsets):
        # L = f.tell()
        #print(L, offsets[i])
        #assert(L == offsets[i])

        "x" / Int8ul,
        "s1" / Int16ul,
        "s2" / Int8ul,
        #print("    x9/xg[%d] x=0x%X (&0x40=%d &1=%d) s1=0x%X (/0x20=%d) s2=0x%X" % (i, x, x&0x40, x&1, s1, s1//0x20, s2), end="")
        #assert(x in [0x01, 0xC0, 0xC1, 0xE0, 0xA0])
        #assert(s1 in [0x0, 0x7, 0x20, 0x40, 0x60, 0x80, 0xA0, 0xC0, 0xE0, 0x100, 0x120])

        # This is probably a bitmask.
        # Every object with bit 0x40 seems to have a position

        Switch(this._.x, {
            0x00: T00,
            0x01: T01,
            
            0x10: T10,
            0x11: T11,
        
            0x20: T20,
            0x21: T21,

            0x30: T30,
            0x31: T31,

            0x40: T40,
            0x41: T41,
                    
            0x50: T50,
        
            0x60: T60,
            0x61: T61,

            0x80: T80,
            0x81: T81,

            0x82: T82,
                
            0x90: T90,
            0x91: T91,

            0xA0: TA0,
            0xA1: TA1,

            0xB0: TB0,
            0xB1: TB1,
            
            0xC0: TC0,
            0xC1: TC1,

            0xD0: TD0,
            0xD1: TD1,            

            0xE0: TE0,
            0xE1: TE1,

            0xF0: TF0,
            0xF1: TF1,

        })
        
        #print("%s" % (i, x.hex()))
    )
    #FIXME: assert(f.tell() == len(d))
)

# Offsets into x9/xg data buffer (offset must be multiplied by 4)
dumpx11 = GreedyRange(
    Struct(
        #L = f.tell()
        "x" / Int16ul,
        #print("    x11/xi[%d] x=%d (*4=%d) // %d" % (i, x, x*4, L))
        #offsets += [x*4]
    )
    #FIXME: assert(f.tell() == len(d))
)


dumpxe = dumpx7
dumpxg = dumpx9
dumpxi = dumpx11

def skipUntil(offset, name):
    lName = "_L_%s" % name
    return ("pad_%s" % name) / Struct(
        lName / Tell,
        "Skipped" / Struct("data" / Bytes(offset - this._[lName]))
    )

def skipUntil_legacy(offset, name, index=0):
    i = index
    assert(f.tell() <= offset)
    if f.tell() == offset:
        print("Skip %s is empty!" % name)
    else:
        print("Warning: %s not empty!" % name)
    d = [None] * index
    while f.tell() < offset:
        o = f.tell()
        "x" / Int32ul
        print("%d/%d: %s[%d] 0x%X ~ %d" % (o, o % 4, name, i, x, x))
        d += [x]
        i += 1
    print("Seeking to offset!")
    f.seek(offset)
    return d

Boobs = Struct(
    "magic" / Const(b'LBH0'),

    # Contains headers
    "aaa0" / Int32ul,
    "aaa1" / Float32l,
    #print("aaa0=%d aaa1=%f" % (aaa0, aaa1))
    #assert(aaa0 == 5)
    "aaa2" / Int32ul,
    "aaa3" / Int32ul,
    #print("aaa2=%d aaa3=%d" % (aaa2, aaa3))
    #assert(aaa2 == 0)
    #assert(aaa3 == 0)
    "aaa4" / Int32ul,
    "aaa5" / Int32ul,
    #print("aaa4=%d aaa5=%d" % (aaa4, aaa5))
    "tilesOffset" / Int32ul,
    "tilesSize" / Int32ul,
    #print("tilesOffset=%d tilesSize=%d" % (tilesOffset, tilesSize))
    #assert(aaa4 == (tilesOffset + tilesSize))
    "aaa8" / Int32ul,
    "aaa9" / Int32ul,
    #print("aaa8=%d aaa9=%d" % (aaa8, aaa9))
    #assert(aaa8 == 0)
    #assert(aaa9 == 0)
    "table1Offset_aaa10" / Int32ul,
    "table1Size_aaa11" / Int32ul,
    #print("table1 offset=%d size=%d" % (table1Offset_aaa10, table1Size_aaa11))
    "table2Offset_aaa12" / Int32ul,
    "table2Size_aaa13" / Int32ul,
    #print("table2 offset=%d size=%d" % (table2Offset_aaa12, table2Size_aaa13))
    "aaa14" / Int32ul,
    "aaa15" / Int32ul,
    #print("aaa14=%d aaa15=%d" % (aaa14, aaa15))
    #assert(aaa15 == 0)

    # This might register some names
    "strings1Offset_aaa16" / Int32ul,
    "strings1Size_aaa17" / Int32ul,
    #print("strings1 offset=%d size=%d" % (strings1Offset_aaa16, strings1Size_aaa17))

    # Points at strings from section 1, or TSceneryDescriptorMultiState.RegistrationName
    "strings2Offset_aaa18" / Int32ul,
    "strings2Size_aaa19" / Int32ul,
    #print("strings2 offset=%d size=%d" % (strings2Offset_aaa18, strings2Size_aaa19))
    #assert(strings2Offset_aaa18 == aaa14)

    #print()
    skipUntil(this._._.tilesOffset, "tiles"),
    #print(tilesSize // 24)
    "tileHeaders" / StructArray(this._.tilesSize // 24, "TileHeader" / Struct(
        "aa" / Int32ul,
        "ab" / Int32ul,
        "tileCountX" / Int32ul,
        "tileCountY" / Int32ul,
        "tileSizeX" / Float32l,
        "tileSizeY" / Float32l
        #assert(aa == 0)
    )),
    skipUntil(this._._.tilesOffset+this._._.tilesSize, "tiles-pad"),

    #print()
    # offset=aaa4, size=aaa5
    skipUntil(this._._.aaa4, "pre4"),
    #assert(aaa5 % 4 == 0)
    "data4" / StructArray(this._.aaa5 // 4, "Data4" / Struct(
        "x" / Int32ul
    )),
    skipUntil(this._._.aaa4 + this._._.aaa5, "in4"),

    
    #print()
    # f.seek(table1Offset_aaa10)
    skipUntil(this._._.table1Offset_aaa10, "pre10"),
    # Some table
    
    "data10" / StructArray(this._.table1Size_aaa11 // ((6+7) * 4), "Data10" / Struct(
        "x0" / Float32l, # X coordinate of tile center?
        "x1" / Float32l, # Y coordinate of tile center?
        "x2" / Float32l, 
        "x3" / Float32l,
        "x4" / Float32l,
        "x5" / Float32l,
        "x6" / Int32ul,
        "x7" / Int32ul, # some offset
        "x8" / Int32ul,
        "x9" / Int32ul, # some offset 
        "x10" / Int32ul,
        "x11" / Int32ul, # some offset to uint16[]?
        "x12" / Int32ul, # size of x11

        #if True:
        #    print("g table1 # OBJ")
        #    print("v %f %f %f # OBJ" % (x0, 0.0, x1))
        #    gx = x0
        #    gy = x1
        #offsets = dumpx11(dump(f, "boobs/x11_%d.bin" % i, x11, x12))
        #dumpx9(dump(f, "boobs/x9_%d.bin" % i, x9, x10), offsets)
        #dumpx7(dump(f, "boobs/x7_%d.bin" % i, x7, x8))

        #assert(x9 == align(x11 + x12, 4))
    )),
    skipUntil(this._._.table1Offset_aaa10 + this._._.table1Size_aaa11, "in10"),

    #print(f.tell())

    # offset=strings1Offset_aaa16 size=strings1Size_aaa17
    skipUntil(this._._.strings1Offset_aaa16, "pre16"),
    "strings1" / StructArray(this._.strings1Size_aaa17 // 64, "String" / String),
    skipUntil(this._._.strings1Offset_aaa16 + this._._.strings1Size_aaa17, "in16"),

    #f.seek(table2Offset_aaa12)
    skipUntil(this._._.table2Offset_aaa12, "pre12"),
    # Blocks of 13*4
    #assert((table2Size_aaa13 % (13 * 4)) == 0)

    "data12" / StructArray(this._.table2Size_aaa13 // (13 * 4), "Data12" / Struct(
        "x" / Int32ul,
        "xb" / Int32ul,
        "xc0" / Float32l,
        "xc1" / Float32l,
        "xc2" / Float32l,
        "xc3" / Float32l,
        "xd" / Int32ul, # Might be 2 uint16?

        "xe" / Int32ul, # some offset
        "xf" / Int32ul, # size of xe
        
        "xg" / Int32ul, # some offset
        "xh" / Int32ul, # size of gh

        "xi" / Int32ul, # some offset
        "xj" / Int32ul, # size of xi

        #if False:
        #    gx = None
        #    gy = None
        #    print("g table2 # OBJ")
        #    print("v %f %f %f # OBJ" % (xc2, 0.0, xc3))
        #offsets = dumpxi(dump(f, "boobs/xi_%d.bin" % i, xi, xj))
        #dumpxg(dump(f, "boobs/xg_%d.bin" % i, xg, xh), offsets)
        #dumpxe(dump(f, "boobs/xe_%d.bin" % i, xe, xf))
        #assert(x == 0)
        #assert(xb == 0)
        #assert(xi == align(xe + xf, 4))
        #assert(xg == align(xi + xj, 4))
        # next_xe = xg+xh
    )),
    skipUntil(this._._.table2Offset_aaa12 + this._._.table2Size_aaa13, "in12"),
    #print("max(xd)", foo)

    # offset=strings2Offset_aaa18 size=strings2Size_aaa19
    skipUntil(this._._.strings2Offset_aaa18, "pre18"),
    "strings2" / StructArray(this._.strings2Size_aaa19 // 64, "String" / String),
    skipUntil(this._._.strings2Offset_aaa18 + this._._.strings2Size_aaa19, "in18")

    #assert(f.tell() == len(data))
)

#Boobs = Debugger(Boobs)


if __name__ == "__main__":
    main = CommonMain(Boobs, "Boobs")
    main.main()
