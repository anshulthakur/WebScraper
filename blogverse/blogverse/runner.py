import sys
import os
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer

path = os.path.dirname(os.path.realpath(__file__))+'/../'
print(path)
sys.path.append(path)


process = CrawlerRunner(get_project_settings())

from blogverse.spiders.general import GeneralSpider
from blogmap.models import Listing
from utils import strip_url
if len(sys.argv)<2:
  print('Usage:\n python {} <domain url/seed>'.format(__file__))
  exit()

domain = sys.argv[1]
print('crawling {}'.format(domain))

@defer.inlineCallbacks
def crawl(domain):
    yield process.crawl('general', urls=domain)
    #Now that we've finished crawling the seed URL, iterate through the other domains found and parse them too.
    url = Listing.objects.get(url=strip_url(domain))
    urls = Listing.objects.exclude(url__contains=url.domain.url)
    for url in urls:
      yield process.crawl('general', urls=url.url)
    reactor.stop()

crawl(domain)
reactor.run() # the script will block here until the last crawl call is finished
