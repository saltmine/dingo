from __future__ import absolute_import
import requests

from .config import settings


def get_file(file_name):
  url = file_name
  if settings.get('url_prefix'):
    url = "%s/%s" % (settings['url_prefix'], file_name)
  requests.get(url).content
