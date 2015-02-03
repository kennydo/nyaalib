import os

import pytest
import requests_mock

from nyaalib import NyaaClient, TorrentNotFoundError

here = os.path.dirname(os.path.abspath(__file__))

def test_invalid_torrent_id():
    nyaa_url = 'http://www.nyaa.se'
    invalid_tid = '486766invalid',

    client = NyaaClient(nyaa_url)
    with requests_mock.mock() as m:
        mocked_page_output = open(os.path.join(here, 'pages', 'view_tid_not_found.html'), 'r').read()
        m.get(nyaa_url, text=mocked_page_output)

        with pytest.raises(TorrentNotFoundError):
            torrent_page = client.view_torrent(invalid_tid)

def test_valid_torrent_id():
    nyaa_url = 'http://www.nyaa.se'
    valid_tid = '486766',

    client = NyaaClient(nyaa_url)
    with requests_mock.mock() as m:
        mocked_page_output = open(os.path.join(here, 'pages', 'view_tid_486766.html'), 'r').read()
        m.get(nyaa_url, text=mocked_page_output)
        client.view_torrent(valid_tid)

        # TODO: assert the values in the parsed page
