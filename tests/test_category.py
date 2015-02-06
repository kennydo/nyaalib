from nyaalib.torrent import Category


def test_reverse_lookup_of_subcategory():
    assert Category.lookup_category('1_0') == Category.anime
    assert Category.lookup_category('3_14') == Category.audio__lossless_audio


def test_values():
    assert Category.anime.value == '1_0'
    assert Category.audio__lossless_audio.value == '3_14'