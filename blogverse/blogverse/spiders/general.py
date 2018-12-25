# -*- coding: utf-8 -*-
import scrapy
from blogverse.items import GeneralItem

from scrapy.utils.project import get_project_settings
from scrapy.spidermiddlewares.offsite import OffsiteMiddleware

from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

import re
from urllib.parse import urlparse

import blogverse.spiders.filter_rules as filter_rules

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

class GeneralSpider(scrapy.Spider):
  name = "general"
  download_delay = 1.0
  handle_httpstatus_list = [404] #Pass 404 apart from return codes between 200-300

  rules = (Rule(LinkExtractor(deny=filter_rules.filters['deny'])))

  def __init__(self, *args, **kwargs):
    name = kwargs.pop('name', None)
    urls = kwargs.pop('urls', None).split(',')
    super(GeneralSpider, self).__init__(name, **kwargs)
    if urls is not None:
      self.start_urls += urls
      for idx, url in enumerate(self.start_urls):
        if not url.startswith('http://') and not url.startswith('https://'):
          self.start_urls[idx] = 'http://%s/' %url
    
    self.allowed_domains = [re.sub(r'^www\.','', urlparse(url).hostname) for url in self.start_urls]

    #print 'Printing Allowed domains list'
    #print self.allowed_domains

    
  #def start_requests(self):
  #  #urls = ['http://aestheticblasphemy.com',]
  #  urls = []
  #  print('start_requests')
  #  for url in urls:
  #    #Update allowed domains
  #    allowed_domains = [ re.sub(r'^www\.', '', urlparse(url).hostname) for url in urls]
  #    self.change_allowed_domains(allowed_domains)
  #
  #    yield scrapy.Request(url=url, callback=self.parse)

  def change_allowed_domains(self, allowed_domains):
    self.allowed_domains = allowed_domains

    for middleware in self.crawler.engine.scraper.spidermw.middlewares:
        if isinstance(middleware, OffsiteMiddleware):
            middleware.spider_opened(self)

  def parse(self, response):
    #First, create a general item for the current page
    validator = URLValidator()
    page = GeneralItem()
    page['title']=response.css('title::text').extract_first() or ''
    page['url'] = response.url
    page['author'] = None
    try:
      page['parent'] = response.meta['parent']
    except:
      page['parent'] = None

    yield page

    #Then, parse all URLs on this page and make an entry for them
    item = GeneralItem()
    for url in response.xpath('//a/@href').extract():
      try:
        if validator(url) and len(url) > 0 and url.strip()[0] == '/':
          item['url'] = response.urljoin(url)
        else:
          item['url'] = url
      
        if urlparse(url).scheme == '':
          url = 'http://'+url
        item['title'] = None
        item['author'] = None
        item['parent'] = response.url

        yield item
      except ValidationError:
        pass
    #Finally, feed all the  URLs on this page for further parsing
    #if they're of our domain and have not been parsed before
    #this filtering is taken care of by the allowed_domains field.
    for selection in response.xpath('//a'):
        url = selection.xpath('./@href').extract_first()
        try:
          validator(url)
          if url is not None and len(url) > 0:
            if url.strip()[0] == '/':
                item = response.urljoin(url)
            else:
                item = url
            if urlparse(item).scheme == '':
                item = 'http://'+item
            request = scrapy.Request(url=item, callback=self.parse)
            request.meta['parent'] = response.url
            yield(request)
        except:
          pass
