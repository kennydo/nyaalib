import codecs
from xml.etree import ElementTree

import html5lib
import requests

from .torrent import TorrentPage, Torrent

TORRENT_NOT_FOUND_TEXT = u'The torrent you are looking for ' \
                          'does not appear to be in the database.'


class TorrentNotFoundError(Exception):
    pass


class NyaaClient(object):
    """A Nyaa client.

    Provides configuration and methods to access Nyaa.
    """

    def __init__(self, url='http://www.nyaa.se'):
        """Initialize the :class:`NyaaClient`.

        :param url: the base URL of the Nyaa or Nyaa-like torrent tracker
        """
        self.base_url = url

    def _get_page_content(self, response):
        """Given a :class:`requests.Response`, return the
        :class:`xml.etree.Element` of the content `div`.

        :param response: a :class:`requests.Response` to parse
        :returns: the :class:`Element` of the first content `div` or `None`
        """
        document = html5lib.parse(
            response.content,
            encoding=response.encoding,
            treebuilder='etree',
            namespaceHTMLElements=False
        )
        # etree doesn't fully support XPath, so we can't just search
        # the attribute values for "content"
        divs = document.findall(
            ".//body//div[@class]")
        content_div = None
        for div in divs:
            if "content" in div.attrib['class'].split(' '):
                content_div = div
                break

        # The `Element` object is False-y when there are no subelements,
        # so compare to `None`
        if content_div is None:
            return None
        return content_div


    def view_torrent(self, torrent_id):
        """
        :param torrent_id: the ID of the torrent to view
        :raises TorrentNotFoundError: if the torrent does not exist
        """
        params = {
            'page': 'view',
            'tid': torrent_id,
        }
        r = requests.get(self.base_url, params=params)
        content = self._get_page_content(r)

        # Check if the content div has any child elements
        if not len(content):
            # The "torrent not found" text in the page has some unicode junk
            # that we can safely ignore.
            text = str(content.text.encode('ascii', 'ignore'))
            if TORRENT_NOT_FOUND_TEXT in text:
                raise TorrentNotFoundError(TORRENT_NOT_FOUND_TEXT)

        return content

    def get_torrent(self, torrent_id):
        """Gets the `.torrent` data for the given `torrent_id`.

        :param torrent_id: the ID of the torrent to download
        :raises TorrentNotFoundError: if the torrent does not exist
        :returns: :class:`Torrent` of the associated torrent
        """
        params = {
            'page': 'download',
            'tid': torrent_id,
        }
        r = requests.get(self.base_url, params=params)
        if r.headers.get('content-type') != 'application/x-bittorrent':
            raise TorrentNotFoundError(TORRENT_NOT_FOUND_TEXT)
        torrent_data = r.content
        return Torrent(torrent_id, torrent_data)
