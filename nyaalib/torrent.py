class TorrentPage(object):
    def __init__(self, torrent_id, name, submitter, tracker, date_created,
                 seeders, leechers, downloads, file_size, description):
        """
        :param torrent_id: a `str` ID
        :param name: the name of the torrent
        :param submitter: the :class:`User` who submitted the torrent
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
    def __init__(self, user_id, name):
        self.uid = user_id
        self.name = name

    def __repr__(self):
        return "<User uid='{0}' name='{1}'>".format(
            self.uid, self.name)


class Torrent(object):
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

class ListingPage(object):
    pass
