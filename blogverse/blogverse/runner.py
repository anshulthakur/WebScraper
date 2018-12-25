import sys
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

path = os.path.dirname(os.path.realpath(__file__))+'/../'
print(path)
sys.path.append(path)

from blogverse.spiders.general import GeneralSpider

process = CrawlerProcess(get_project_settings())

if len(sys.argv)<2:
  print('Usage:\n python {} <domain url/seed>'.format(__file__))
  exit()

domain = sys.argv[1]
print('crawling {}'.format(domain))
process.crawl('general', urls=domain)
process.start()
