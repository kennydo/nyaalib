from nyaalib import Category


def test_reverse_lookup_of_subcategory():
    assert Category.lookup_category('1_0') == Category.anime
    assert Category.lookup_category('3_14') == Category.audio__lossless_audio


def test_values():
    assert Category.anime.value == '1_0'
    assert Category.audio__lossless_audio.value == '3_14'


def test_lookup_invalid_values():
    assert Category.lookup_category('not_a_real_value') is None
    assert Category.lookup_category('1_panda') is None
