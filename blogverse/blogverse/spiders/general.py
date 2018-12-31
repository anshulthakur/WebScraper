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

from blogmap.models import Listing, Domain, Linkage
from utils import strip_url

import logging

# get an instance of the logger object this module will use
logger = logging.getLogger("blogverse")


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

  def change_allowed_domains(self, allowed_domains):
    self.allowed_domains = allowed_domains

    for middleware in self.crawler.engine.scraper.spidermw.middlewares:
        if isinstance(middleware, OffsiteMiddleware):
            middleware.spider_opened(self)

  def parse(self, response):
    #First, create a general item for the current page
    try:
        listing = Listing.objects.get(url=strip_url(response.url))
        if listing.crawled == True:
          return #Don't parse it
    except Listing.DoesNotExist:
        pass

    #print(response.url)
    logger.info('{}'.format(response.url))
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
    #page = self.process_item(page)
    
    #Then, parse all URLs on this page and make an entry for them if they aren't this domain's
    for url in response.xpath('//a/@href').extract():
      try:
        if len(url) > 0 and url.strip()[0] == '/':
          url = response.urljoin(url)
        validator(url)
        if urlparse(url).scheme == '':
          url = 'http://'+url
        if urlparse(url).hostname != urlparse(response.url).hostname:
          item = GeneralItem()
          item['url'] = url
          item['title'] = None
          item['author'] = None
          item['parent'] = response.url
          yield item
          #self.process_item(item)
      except ValidationError:
        pass
    #Finally, feed all the  URLs on this page for further parsing
    #if they're of our domain and have not been parsed before
    #this filtering is taken care of by the allowed_domains field.
    for selection in response.xpath('//a'):
      url = selection.xpath('./@href').extract_first()
      try:
        if len(url) > 0 and url.strip()[0] == '/':
          url = response.urljoin(url)
        validator(url)
        if urlparse(url).scheme == '':
          url = 'http://'+url
        #Check if the URL already exists in DB. 
        #If it does, we don't want to parse it because we already did last time.
        try:
          obj = Listing.objects.get(url=strip_url(url))
          #print('skip {}'.format(obj.url))
        except Listing.DoesNotExist:
          #print('parse {}'.format(url))
          request = scrapy.Request(url=url, callback=self.parse)
          request.meta['parent'] = response.url
          yield(request)
      except:
        pass
    try:
      listing = Listing.objects.get(url=strip_url(response.url))
      listing.crawled = True
      listing.save()
    except Listing.DoesNotExist:
      #print('Awkward: {} must have existed'.format(strip_url(response.url)))
      logger.info('Awkward: {} must have existed'.format(strip_url(response.url)))
