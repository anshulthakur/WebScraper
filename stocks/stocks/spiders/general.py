# -*- coding: utf-8 -*-
import scrapy
import scrapy_splash
from scrapy_splash import SplashRequest
from stocks.items import GeneralItem

from scrapy.utils.project import get_project_settings
from scrapy.spidermiddlewares.offsite import OffsiteMiddleware

from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

import re
from urlparse import urlparse

import filter_rules

class GeneralSpider(scrapy.Spider):
  name = "general"
  download_delay = 1.0
  handle_httpstatus_list = [404] #Pass 404 apart from return codes between 200-300

  rules = (Rule(LinkExtractor(deny=filter_rules.filters['deny'])))

  def __init__(self, urls=None, *args, **kwargs):
    name = kwargs.pop('name', None)
    super(GeneralSpider, self).__init__(name, **kwargs)
    if urls is not None:
      self.start_urls += urls
      for idx, url in enumerate(self.start_urls):
        if not url.startswith('http://') and not url.startswith('https://'):
          self.start_urls[idx] = 'http://%s/' %url
    
    self.allowed_domains = [re.sub(r'^www\.','', urlparse(url).hostname) for url in self.start_urls]

    print 'Printing Allowed domains list'
    print self.allowed_domains

    
  def start_requests(self):
    urls = ['http://aestheticblasphemy.com',]
    
    for url in urls:
      #Update allowed domains
      allowed_domains = [ re.sub(r'^www\.', '', urlparse(url).hostname) for url in urls]
      self.change_allowed_domains(allowed_domains)

      yield SplashRequest(url, self.parse,
                          args = {
                            'wait': 0.5,
                            'timeout' : 120,
                          },
                          endpoint = 'render.html',
                          slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,
                          )

  def change_allowed_domains(self, allowed_domains):
    self.allowed_domains = allowed_domains

    for middleware in self.crawler.engine.scraper.spidermw.middlewares:
        if isinstance(middleware, OffsiteMiddleware):
            middleware.spider_opened(self)

  def parse(self, response):
    #Right now, all I want to do is make a list of URLs that can be accessed from mere crawling

    # for selection in response.xpath('//a'):
    #   if selection.xpath('./@href').extract():
    #     item = GeneralItem()
    #     item['title']= selection.xpath('text()').extract()
    #     item['url'] = selection.xpath('./@href').extract()
    #     yield item
    #A generator kind of remembers the entire thing, so when we finally break out, we get to next line of code.
    #filters = filter_rules.filters['deny']

    #compound = "(" + ")|(".join(filters)+")"

    #Now, we also want to feed our crawler new URLs
    for selection in response.xpath('//a'):
      if selection.xpath('./@href').extract():
        #if re.match(compound, selection.xpath('./@href').extract()[0]) is None:
        item = response.urljoin(selection.xpath('./@href').extract()[0])
        yield SplashRequest(item, self.parse,
                          args = {
                            'wait': 0.5,
                            'timeout' : 120,
                          },
                          endpoint = 'render.html',
                          slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,
                          )

    #Save the URL of response
    item = GeneralItem()
    item['title'] = response.css('title::text').extract()[0]
    item['url'] = response.url
    item['desc'] = response.status
    yield item

