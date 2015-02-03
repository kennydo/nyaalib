class TorrentPage(object):
    def __init__(self, torrent_id, name, submitter, tracker, date_created,
                 seeders, leechers, downloads, file_size):
        self.tid = torrent_id
        self.name = name
        self.submitter = submitter
        self.tracker = tracker
        self.date_created = date_created
        self.seeders = seeders
        self.leechers = leechers
        self.downloads = downloads
        self.file_size = file_size


class Torrent(object):
    def __init__(self, torrent_id, torrent_data):
        self.tid = torrent_id
        self.data = torrent_data

    def __repr__(self):
        return "<Torrent tid='{0}' with {1} character body>".format(
            self.tid, len(self.data))

class ListingPage(object):
    pass
