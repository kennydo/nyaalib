import datetime
from xml.etree import ElementTree

import html5lib
import requests

from .models import Category, TorrentPage, Torrent, User

TORRENT_NOT_FOUND_TEXT = \
    u'The torrent you are looking for does not appear to be in the database.'


class TorrentNotFoundError(Exception):
    pass


class NyaaClient(object):
    """The Nyaa client.

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
        """Retrieves and parses the torrent page for a given `torrent_id`.

        :param torrent_id: the ID of the torrent to view
        :raises TorrentNotFoundError: if the torrent does not exist
        :returns: a :class:`TorrentPage` with a snapshot view of the torrent
            detail page
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

        cell_td_elems = content.findall('.//td')
        name = cell_td_elems[3].text

        category_href = content\
            .findall(".//td[@class='viewcategory']/a[2]")[0]\
            .attrib['href']
        category_value = category_href.split('cats=')[1]
        category = Category.lookup_category(category_value)

        # parse the submitter details
        submitter_a_elem = cell_td_elems[7].findall('a')[0]
        submitter_id = submitter_a_elem.attrib['href'].split('=')[1]
        submitter_name = submitter_a_elem.findall('span')[0].text
        submitter = User(submitter_id, submitter_name)

        tracker = cell_td_elems[11].text
        date_created = datetime.datetime.strptime(
            cell_td_elems[5].text, '%Y-%m-%d, %H:%M %Z')

        seeders = int(content.findall(".//span[@class='viewsn']")[0].text)
        leechers = int(content.findall(".//span[@class='viewln']")[0].text)
        downloads = int(content.findall(".//span[@class='viewdn']")[0].text)

        file_size = cell_td_elems[21].text

        # note that the tree returned by html5lib might not exactly match the
        # original contents of the description div
        description = ElementTree.tostring(
            content.findall(".//div[@class='viewdescription']")[0],
            encoding='utf8', method='html')
        return TorrentPage(
            torrent_id, name, submitter, category, tracker, date_created, seeders,
            leechers, downloads, file_size, description)

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
