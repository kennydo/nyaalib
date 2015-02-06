import enum


@enum.unique
class Category(enum.Enum):
    """An enumeration of the categories on Nyaa.
    There are top level categories (eg: `anime`) and sub categories
    (eg: `anime__anime_music_video`).

    Nyaa allows searching by either top level category alone
    or top level and sub category, so both are included in this enumeration,
    with the sub categories prefixed by the top level category and two
    underscores.
    """
    all_categories = '0_0'

    anime = '1_0'
    anime__anime_music_video = '1_32'
    anime__english_translated_anime = '1_37'
    anime__non_english_translated_anime = '1_38'
    anime__raw_anime = '1_11'

    audio = '3_0'
    audio__lossless_audio = '3_14'
    audio__lossy_audio = '3_15'

    literature = '2_0'
    literature__english_translated_literature = '2_12'
    literature__non_english_translated_literature = '2_39'
    literature__raw_literature = '2_13'

    live_action = '5_0'
    live_action__english_translated_live_action = '5_19'
    live_action__live_action_promotional_video = '5_22'
    live_action__non_english_translated_live_action = '5_21'
    live_action__raw_live_action = '5_20'

    pictures = '4_0'
    pictures__graphics = '4_18'
    pictures__photos = '4_17'

    software = '6_0'
    software__applications = '6_23'
    software__games = '6_24'

    art = '7_0'
    art__anime = '7_25'
    art__doujinshi = '7_33'
    art__games = '7_27'
    art__manga = '7_26'
    art__pictures = '7_28'

    real_life = '8_0'
    real_life__photobooks_and_pictures = '8_31'
    real_life__videos = '8_30'

    @classmethod
    def lookup_category(cls, value):
        """Given the Nyaa category in number, underscore, number form,
        return the appropriate :class:`Category`, or `None`.

        :param value: Nyaa category in `number_number` form (eg: '1_0')
        :return: :class:`Category` or `None`
        """
        return cls._value2member_map_.get(value, None)


class TorrentPage(object):
    """Represents a snapshot view of a torrent detail page

    Some of the instance variables do not change over time (eg: `name`,
    `submitter`, `category`, etc.), but some variables do change
    (eg: the number of `seeders`, the number of `leechers`).
    """
    def __init__(self, torrent_id, name, submitter, category, tracker,
                 date_created, seeders, leechers, downloads, file_size,
                 description):
        """
        :param torrent_id: a `str` ID
        :param name: the name of the torrent
        :param submitter: the :class:`User` who submitted the torrent
        :param category: the :class:`Category` of the torrent
        :param tracker: URI of the tracker
        :param date_created: a :class:`datetime.datetime`
        :param seeders: the current `int` number of seeders
        :param leechers: the `current int` number of leechers
        :param downloads: the cumulative `int` number of downloads
        :param file_size: a `str` describing the file size
        :param description: the `str` description provided by the uploader
        """
        self.tid = torrent_id
        self.name = name
        self.submitter = submitter
        self.category = category
        self.tracker = tracker
        self.date_created = date_created
        self.seeders = seeders
        self.leechers = leechers
        self.downloads = downloads
        self.file_size = file_size
        self.description = description

    def __repr__(self):
        return "<TorrentPage tid='{0}' name='{1}'>".format(
            self.tid, self.name)


class User(object):
    """Represents a Nyaa user.
    """
    def __init__(self, user_id, name):
        self.uid = user_id
        self.name = name

    def __repr__(self):
        return "<User uid='{0}' name='{1}'>".format(
            self.uid, self.name)


class Torrent(object):
    """Holds the Nyaa ID of the torrent, as well as the contents of the
    `.torrent` file.
    """
    def __init__(self, torrent_id, torrent_data):
        """
        :param torrent_id: a `str` ID
        :param torrent_data: a `str` containing the contents of the `.torrent`
            file
        """
        self.tid = torrent_id
        self.data = torrent_data

    def __repr__(self):
        return "<Torrent tid='{0}' with {1} character body>".format(
            self.tid, len(self.data))
