from urllib.parse import urlparse
import re

def strip_url(url):
  parsed = urlparse(url)
  url = re.sub(r'^www\.','', parsed.hostname)
  if parsed.path != '/':
    url = url + parsed.path
  return url
