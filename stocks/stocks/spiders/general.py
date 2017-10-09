# -*- coding: utf-8 -*-
import scrapy
import scrapy_splash
from scrapy_splash import SplashRequest
from stocks.items import GeneralItem

from scrapy.utils.project import get_project_settings
from scrapy.spidermiddlewares.offsite import OffsiteMiddleware

import re
from urlparse import urlparse

class GeneralSpider(scrapy.Spider):
  name = "general"
  
  def __init__(self, *args, **kwargs):
    super(GeneralSpider, self).__init__()
    
    self.url_list = []
    self.allowed_domains = []

    
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
    #Save the URL of response
    print response.url
    #Right now, all I want to do is make a list of URLs that can be accessed from mere crawling

    # for selection in response.xpath('//a'):
    #   if selection.xpath('./@href').extract():
    #     item = GeneralItem()
    #     item['title']= selection.xpath('text()').extract()
    #     item['url'] = selection.xpath('./@href').extract()
    #     yield item
    #A generator kind of remembers the entire thing, so when we finally break out, we get to next line of code.

    #Now, we also want to feed our crawler new URLs
    for selection in response.xpath('//a'):
      if selection.xpath('./@href').extract():
        item = response.urljoin(selection.xpath('./@href').extract()[0])
        yield SplashRequest(item, self.parse,
                          args = {
                            'wait': 0.5,
                            'timeout' : 120,
                          },
                          endpoint = 'render.html',
                          slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,
                          )

