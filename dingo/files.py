import requests

from config import settings

def get_file(file_name):
  url = file_name
  if settings.get('url_prefix'):
    url = "%s/%s" % (settings['url_prefix'], file_name)
  content = None
  try:
    resp = requests.get(url)
    content = resp.content
  except:
    raise
  return content

