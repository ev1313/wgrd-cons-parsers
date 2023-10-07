from tests.declarativeunittest import xfail
from wgrd_cons_parsers.mesh import Mesh

@xfail(reason="mesh.py is not building yet")
def test_mesh():
    mesh_path = "files/Maps/WarGame/PC/CampDyn_ClimbNarodnaia_v11.dat/surfaces/zones.mesh"
    in_file = open(mesh_path, "rb").read()
    data = Mesh.parse(in_file)
    preprocessed, _ = Mesh.preprocess(data)
    out_data = Mesh.build(preprocessed)
    assert in_file == out_data
