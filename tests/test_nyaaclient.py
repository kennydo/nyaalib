import codecs
import datetime
import os

import pytest
import requests_mock

from nyaalib import (
    Category, NyaaClient, SearchOrderKey, SearchSortKey, TorrentNotFoundError,
)


here = os.path.dirname(os.path.abspath(__file__))
nyaa_url = 'http://www.nyaa.se'

def get_page_contents(filename):
    file_path = os.path.join(here, 'pages', filename)
    with codecs.open(file_path, encoding='utf-8') as f:
        return f.read()


def test_invalid_torrent_id():
    invalid_tid = '486766invalid',

    client = NyaaClient(nyaa_url)
    with requests_mock.mock() as m:
        mocked_page_output = get_page_contents('view_tid_not_found.html')
        m.get(nyaa_url, text=mocked_page_output)

        with pytest.raises(TorrentNotFoundError):
            client.view_torrent(invalid_tid)


def test_valid_torrent_id():
    valid_tid = '486766',

    client = NyaaClient(nyaa_url)
    with requests_mock.mock() as m:
        mocked_page_output = get_page_contents('view_tid_486766.html')
        m.get(nyaa_url, text=mocked_page_output)
        torrent_page = client.view_torrent(valid_tid)

    assert torrent_page.tid == valid_tid
    assert torrent_page.name == '[FFF] Love Live! [BD][720p-AAC]'
    assert torrent_page.category == Category.anime__english_translated_anime
    assert torrent_page.submitter.uid == '73859'
    assert torrent_page.submitter.name == 'FFF'
    assert torrent_page.tracker == \
        'http://open.nyaatorrents.info:6544/announce'
    assert torrent_page.date_created == datetime.datetime(2013, 10, 26, 7, 9)
    assert torrent_page.seeders == 47
    assert torrent_page.leechers == 12
    assert torrent_page.downloads == 17786
    assert torrent_page.file_size == '6.72 GiB'


def test_no_torrents_found():
    client = NyaaClient(nyaa_url)
    with requests_mock.mock() as m:
        mocked_page_output = get_page_contents('search_no_torrents_found.html')
        m.get(nyaa_url, text=mocked_page_output)
        m.encoding = 'utf-8'
        search_result_page = client.search('no_torrents_found')

    assert search_result_page.page == 1
    assert search_result_page.total_pages == 1
    assert len(search_result_page.torrent_stubs) == 0


def test_search_sort_by_seeders_descending():
    client = NyaaClient(nyaa_url)
    with requests_mock.mock() as m:
        mocked_page_output = get_page_contents(
            'search_love_live_seeders_descending.html')
        m.get(nyaa_url, text=mocked_page_output)
        m.encoding = 'utf-8'
        search_result_page = client.search(
            'love live', category=Category.anime__english_translated_anime,
            sort_key=SearchSortKey.seeders,
            order_key=SearchOrderKey.descending)

    assert search_result_page.page == 1
    assert search_result_page.total_pages == 3
    assert len(search_result_page.torrent_stubs) == 100

    previous_stub = search_result_page.torrent_stubs[0]
    for stub in search_result_page.torrent_stubs[1:]:
        # This test page doesn't exhibit it, but the number of seeders and
        # leechers are sometimes unavailable, so they can be `None`.
        assert previous_stub.seeders >= stub.seeders
        previous_stub = stub


def test_search_sort_by_seeders_ascending():
    client = NyaaClient(nyaa_url)
    with requests_mock.mock() as m:
        mocked_page_output = get_page_contents(
            'search_love_live_seeders_ascending.html')
        m.get(nyaa_url, text=mocked_page_output)
        m.encoding = 'utf-8'
        search_result_page = client.search(
            'love live', category=Category.anime__english_translated_anime,
            sort_key=SearchSortKey.seeders,
            order_key=SearchOrderKey.ascending)

    assert search_result_page.page == 1
    assert search_result_page.total_pages == 3
    assert len(search_result_page.torrent_stubs) == 100

    previous_stub = search_result_page.torrent_stubs[0]
    for stub in search_result_page.torrent_stubs[1:]:
        # Sometimes the number of seeders and leechers are `None`, since they
        # are unavailable.
        if previous_stub.seeders is not None and stub.seeders is not None:
            assert previous_stub.seeders <= stub.seeders
        previous_stub = stub