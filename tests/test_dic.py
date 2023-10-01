from wgrd_cons_parsers.dic import Dic
def test_dic_jpn():
    dic_path = "files/Data/WARGAME/PC/49964/58710/ZZ_Win.dat/pc/localisation/jpn/localisation/interface_outgame.dic"
    in_file = open(dic_path, "rb").read()
    data = Dic.parse(in_file)
    preprocessed, _ = Dic.preprocess(data)
    out_data = Dic.build(preprocessed)
    assert in_file == out_data
