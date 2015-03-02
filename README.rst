nyaalib
=======

A simple Python library for parsing Nyaa pages.

Usage
=====

.. code:: python

  >>> from nyaalib import NyaaClient
  >>> client = NyaaClient()
  >>> search_result_page = client.search("love live")
  >>> search_result_page.torrent_stubs[0]
  <TorrentStub tid='661029' name=u'Love Live Music Collection Ver.1.0'>
  >>> torrent_page = client.view_torrent('486766')
  >>> torrent_page.name
  u'[FFF] Love Live! [BD][720p-AAC]'
