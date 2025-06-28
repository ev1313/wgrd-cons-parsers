#!/usr/bin/env python3

from wgrd_cons_parsers.common import *
from conshex import *

Gdp0 = Struct(
        "magic" / Const(b'GDP0'),
        "unk0" / Const(0, Int32ul),
        "_size" / Rebuild(Int32ul, lambda ctx: 12+(len(ctx.entries)*16)),
        "unk1" / Int32ul,
        "_entryCount" / Rebuild(Int32ul, len_(this.entries)),
        "entries" / Array(this._entryCount, "Entry" / Struct(
            "x" / Float32l, # x coordinate
            "y" / Float32l, # y coordinate
            "c" / Float32l, # unknown (doesn't seem to be altitude)
            "d" / Const(1, Int32ul),
        )),
        "unk3" / Const(0, Int32ul),
)

Scenario = Struct(
    "magic" / Const(b'SCENARIO\r\n'),
    "unk" / Bytes(16),
    "unk0a" / Int16ul,
    "unk1" / Int32ul,
    "unk2" / Int32ul,
    "_ndfOffset" / Rebuild(Int32ul, lambda ctx: ctx._offset_ndfbin - 40),
    "areaMagic" / Const(b'AREA'),
    "unkValue" / Int32ul,
    "unkLength" / Int32ul,
    "_entryCount" / Rebuild(Int32ul, len_(this.entries)), #FIXME: Always 4?!
    "entries" / Array(this._entryCount, "Entry" / Struct(
        "_zoneCount" / Rebuild(Int32ul, len_(this.zones)),
        "zones" / Array(this._zoneCount, "Zone" / Struct(
            "area0" / Struct(
                "magic" / Const(b'AREA'),
                "x0" / Int32ul,
                "unk1" / Int32ul,
                "_length" / Rebuild(Int32ul, len_(this.s)),
                "s" / Aligned(4, PaddedString(this._length, 'utf-8')),
            ),
            "area1" / Struct(
                "magic" / Const(b'AREA'),
                "px" / Float32l,
                "py" / Float32l,
                "pz" / Float32l
            ),
            "area2" / Struct(
                "magic" / Const(b'AREA'),
                "_unknownsCount" / Rebuild(Int32ul, len_(this.unknowns)), # enohka: Subpart count
                "unknowns" / Array(this._unknownsCount, "Unknown" / Struct(            
                    "triangleIndex" / Int32ul,
                    "triangleCount" / Int32ul,
                    "vertexIndex" / Int32ul,
                    "vertexCount" / Int32ul,
                ))
            ),
            # Border faces
            "area3" / Struct(
                "magic" / Const(b'AREA'),
                "triangleIndex" / Int32ul,
                "triangleCount" / Int32ul,
                "vertexIndex" / Int32ul,
                "vertexCount" / Int32ul,
            ),
            # Border vertices
            "area4" / Struct(
                "magic" / Const(b'AREA'),
                "vertexOffset" / Int32ul, # enohka: Vertex offset
                "vertexCount" / Int32ul, # enohka: Vertex count
            ),
            # Vertexbuffer?
            "area5" / Struct(
                "magic" / Const(b'AREA'),
                "_vertexCount" / Rebuild(Int32ul, len_(this.vertices)),
                "_faceCount" / Rebuild(Int32ul, len_(this._.area6.faces)),
                "vertices" / Array(this._vertexCount, "Vertex" / Struct(            
                    "vt0" / Float32l,
                    "vt1" / Float32l,
                    "vt2" / Float32l,
                    "vt3" / Float32l,
                    "vt4" / Float32l
                ))
            ),
            # Indexbuffer?
            "area6" / Struct(
                "magic" / Const(b'AREA'),
                "faces" / Array(this._.area5._faceCount, "Face" / Struct(            
                    "ia" / Int32ul,
                    "ib" / Int32ul,
                    "ic" / Int32ul
                ))
            ),
            "area7" / Struct(
                "magic" / Const(b'AREA'),
                "v0" / Const(0, Int32ul), # Always 0?
            ),
            "area8" / Struct(
                "magic" / Const(b'AREA')
            ),
            "end0" / Const(b'END0')
        ))
    )),

    "ndfbin" / Struct(
        "_size" / Rebuild(Int32ul, len_(this.data)),
        "data" / Bytes(this._size),
    ),
    # Firing points while inside a building (1 to 6-ish per building, in corners or along the walls)
    "gdp0" / Struct(
        "_size" / Rebuild(Int32ul, this._size_data),
        "data" / Gdp0
    )
)

if __name__ == "__main__":
    main = CommonMain(Scenario, "Scenario")
    main.main()
