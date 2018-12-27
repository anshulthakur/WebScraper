# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import signals
from scrapy.exceptions import DropItem

#import settings
from blogmap.models import Domain, Listing
from urllib.parse import urlparse
import re
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
      parsed_url = urlparse(item['url'])
      url = re.sub(r'^www\.', '', urlparse(item['url']).hostname)
      if urlparse(item['url']).path !='/':
        url = url+urlparse(item['url']).path
      #print('URL {}\tParent {}'.format(url, item.get('parent', None) ))
      try:
        domain = Domain.objects.get(url=re.sub(r'^www\.', '', parsed_url.hostname))

        if item['title'] is not None and item['title'] !='' and domain.name=='' and parsed_url.path=='':
          domain.name=item['title']
          domain.save()
      except Domain.DoesNotExist:
        #Set title if title is provided and we aren't a subtree node.
        if parsed_url.path=='' or parsed_url.path=='/':
          name=item['title'] or ''
        else:
          name=''
        domain = Domain(url=re.sub(r'^www\.', '', parsed_url.hostname), name=name)
        domain.save()

      #Validate existence of the URL in our tables. If it does, don't create entry.
      try:
        listing = Listing.objects.get(url=url)
      except Listing.DoesNotExist:
        listing = Listing(url=url,
                          domain=domain,
                          title=item['title'] or '')
        listing.save()
        #print(listing.url)
       
      if item['parent'] is not None:
        parent=re.sub(r'^www\.', '', urlparse(item['parent']).hostname)
        if urlparse(item['parent']).path!='/':
            parent = parent+urlparse(item['parent']).path
        #print('Parent: {}'.format(parent))
        listing.links.add(Listing.objects.get(url=parent))

      return item
