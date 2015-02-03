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
        :class:`lxml.etree.Element` of the first content `div`.

        :param response: a :class:`requests.Response` to parse
        :returns: the :class:`Element` of the first content `div` or `None`
        """
        document = html5lib.parse(
            response.content,
            encoding=response.encoding,
            treebuilder='lxml',
            namespaceHTMLElements=False
        )
        content_div = document.xpath(
            "//body//div[contains(concat(' ', @class, ' '), ' content ')][1]")
        if not content_div:
            print response.content
            return None
        return content_div[0]


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

        if content.text and content.text.strip() == TORRENT_NOT_FOUND_TEXT:
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
