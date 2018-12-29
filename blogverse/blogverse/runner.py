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
from django.db.models import Q

if len(sys.argv)<2:
  print('Usage:\n python {} <domain url/seed>'.format(__file__))
  exit()

domain = sys.argv[1]
print('crawling {}'.format(domain))

@defer.inlineCallbacks
def crawl(domain):
    yield process.crawl('general', urls=domain)
    #Just for checks, find all URLs in this domain that remain to be crawled
    try:
      url = Listing.objects.get(url=strip_url(domain))
      urls = Listing.objects.filter(crawled=False, url__contains=url.domain.url)
      for url in urls:
        yield process.crawl('general', urls=url.url)
    except Listing.DoesNotExist:
        print('Listing does not exist')
    except:
        print('Something happened while getting unparsed URLs from the domain')
        for line in sys.exc_info():
          print("{}", line)
    #Now that we've finished crawling the seed URL, iterate through the other domains found and parse them too.
    try:
      from spiders.filter_rules import exclude_domains

      filters = [Q(url__contains=f) for f in exclude_domains]

      query = filters.pop()

      for q in filters:
          query |= q
      urls = Listing.objects.exclude(url__contains=url.domain.url, crawled=True).exclude(query)
      #For now, favour blogpages that have a .blogspot or a wordpress in them first.
      url1 = urls.filter(Q(url__contains="blogspot")|Q(url__contains="wordpress"))
      for url in url1:
        yield process.crawl('general', urls=url.url)
      
      urls = urls.exclude(id__in=url1)
      for url in urls:
        yield process.crawl('general', urls=url.url)
    except:
        for line in sys.exc_info():
          print("{}", line)
    reactor.stop()

crawl(domain)
reactor.run() # the script will block here until the last crawl call is finished
