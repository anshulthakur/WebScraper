# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import signals
from scrapy.exceptions import DropItem

#import settings
from blogmap.models import Domain, Listing, Linkage
from urllib.parse import urlparse
from utils import strip_url

class GeneralSpiderPipeline(object):
    def __init__(self):
      self.files={}

    @classmethod
    def from_crawler(cls, crawler):
      pipeline = cls()
      crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
      crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
      return pipeline

    def spider_opened(self, spider):
      pass

    def spider_closed(self, spider):
      pass

    def process_item(self, item, spider):
      #If the parent domain is new, make that entry too.
      url = strip_url(item['url'])
      parsed_url = urlparse(item['url']) #http:// once lost causes urlparse to not detect netloc etc. properly. It puts everything in path
      #print('Process {}'.format(url))
      try:
        domain = Domain.objects.get(url=parsed_url.hostname)

        if item['title'] is not None and item['title'].strip() !='' and domain.name=='' and (parsed_url.path=='' or parsed_url.path=='/'):
          domain.name=item['title'].strip()
          domain.save()
      except Domain.DoesNotExist:
        #Set title if title is provided and we aren't a subtree node.
        if (parsed_url.path=='' or parsed_url.path=='/') and (item['title'] != None):
          name=item['title'].strip() or ''
        else:
          name=''
        domain = Domain(url=parsed_url.hostname, name=name)
        domain.save()

      #Validate existence of the URL in our tables. If it does, don't create entry.
      try:
        listing = Listing.objects.get(url=url)
      except Listing.DoesNotExist:
        listing = Listing(url=url,
                          domain=domain,
                          title=item['title'] or '')
        listing.save()
       
      if item['parent'] is not None:
        parent = strip_url(item['parent'])
        #print('Parent: {}'.format(parent))
        try:
          linkage = Linkage.objects.get(source=Listing.objects.get(url=parent), destination=listing)
          linkage.frequency +=1
          linkage.save()
        except Linkage.DoesNotExist:
          Linkage.objects.create(source=Listing.objects.get(url=parent), destination=listing)

      return item
