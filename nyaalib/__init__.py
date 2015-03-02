import datetime
from xml.etree import ElementTree
try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    # Python 2
    from urlparse import urlparse, parse_qs

import html5lib
import requests

from .models import (
    Category, SearchSortKey, SearchOrderKey, SearchResultPage, TorrentPage,
    Torrent, TorrentStub, User
)

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

    def search(self, terms, category=Category.all_categories, page=1,
               sort_key=SearchSortKey.date,
               order_key=SearchOrderKey.descending):
        """Get a list of torrents that match the given search term

        :param terms: the `str` needle
        :param category: the desired :class:`Category` of the results
        :param page: the 1-based page to return the result
        :param sort_key: the :class:`SearchSortKey` of the results list
        :param order_key: the :class:`SearchOrderkey` of the results list
        :return: a :class:`SearchPage` of results
        """
        params = {
            'page': 'search',
            'term': terms,
            'cats': category.value,
            'sort': sort_key.value,
            'order': order_key.value,
        }
        r = requests.get(self.base_url, params=params)
        content = self._get_page_content(r)

        # first, get the total number of pages returned. this findall returns
        # two results (one from the top half of the page, one from the bottom),
        # so only take the first element.
        a_to_last_page = content.findall('.//div[@class="rightpages"]/a[2]')
        if not a_to_last_page:
            total_pages = 1
        else:
            last_page_url = a_to_last_page[0].attrib['href']
            offset = extract_url_query_parameter(last_page_url, "offset")[0]
            total_pages = int(offset)

        torrent_stubs = []
        rows = (x for x in content.findall('.//table//tr')
                if 'tlistrow' in x.attrib.get('class', ''))
        for row in rows:
            cell_td_elems = row.findall('td')

            category_value = extract_url_query_parameter(
                cell_td_elems[0].find('a').attrib['href'],
                'cats')[0]
            category = Category.lookup_category(category_value)
            torrent_id = extract_url_query_parameter(
                cell_td_elems[1].find('a').attrib['href'],
                "tid")[0]
            name = cell_td_elems[1].find('a').text
            file_size = cell_td_elems[3].text
            if cell_td_elems[4].text.isdigit():
                seeders = int(cell_td_elems[4].text)
            else:
                seeders = None
            if cell_td_elems[5].text.isdigit():
                leechers = int(cell_td_elems[5].text)
            else:
                leechers = None
            downloads = int(cell_td_elems[6].text)

            stub = TorrentStub(torrent_id, name, category,seeders, leechers,
                               file_size, downloads)
            torrent_stubs.append(stub)
        return SearchResultPage(
            terms, category, sort_key, order_key, page, total_pages,
             torrent_stubs)


def extract_url_query_parameter(url, parameter):
    """Given a URL (ex: "http://www.test.com/path?query=3") and a parameter
    (ex: "query"), return the value as a list
    :param url: a `str` URL
    :param parameter: the URL query we went to extract
    :return: a `list` of values for the given query name in the given URL or
        an empty string if the query is not in the URL
    """
    query_string = urlparse(url).query
    return parse_qs(query_string).get(parameter, [])