from wgrd_cons_parsers.edat import EDat

def test_edat():
    edat_path = "files/Data/WARGAME/PC/58710/59095/ZZ_1.dat/allplatforms/sound/pack/mainsound.mpk"
    in_file = open(edat_path, "rb").read()
    data = EDat.parse(in_file)
    preprocessed, _ = EDat.preprocess(data)
    out_data = EDat.build(preprocessed)
    assert in_file == out_data
