import datetime
import os

import pytest
import requests_mock

from nyaalib.client import Category, NyaaClient, TorrentNotFoundError


here = os.path.dirname(os.path.abspath(__file__))


def get_page_contents(filename):
    with open(os.path.join(here, 'pages', filename), 'r') as f:
        return f.read()


def test_invalid_torrent_id():
    nyaa_url = 'http://www.nyaa.se'
    invalid_tid = '486766invalid',

    client = NyaaClient(nyaa_url)
    with requests_mock.mock() as m:
        mocked_page_output = get_page_contents('view_tid_not_found.html')
        m.get(nyaa_url, text=mocked_page_output)

        with pytest.raises(TorrentNotFoundError):
            client.view_torrent(invalid_tid)


def test_valid_torrent_id():
    nyaa_url = 'http://www.nyaa.se'
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
