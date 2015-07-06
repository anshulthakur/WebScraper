'''
Created on 03-Jul-2015

@author: anshul
'''
import re
import scrapy
from urlparse import urlparse

from tutorial.items import GeneralItem


class GeneralSpider(scrapy.Spider):
    name = "General Spider"
    start_urls = []
    allowed_domains = [] #Might be non-mandatory
    
    def __init__(self, urls=None, **kwargs):
        name= kwargs.pop('name', None)        
        super(GeneralSpider, self).__init__(name, **kwargs)
        if urls is not None:
            self.start_urls += urls
            for idx, url in enumerate(self.start_urls):
                if not url.startswith('http://') and not url.startswith('https://'):
                    self.start_urls[idx] = 'http://%s/' % url
                    
        self.allowed_domains = [re.sub(r'^www\.','', urlparse(url).hostname) for url in self.start_urls]
        
        print 'Printing Allower Domains List'
        print self.allowed_domains
        
    def parse(self, response):
        for sel in response.xpath('//a'):
            item = GeneralItem()
            item['title'] = sel.xpath('text()').extract()
            item['url'] = sel.xpath('./@href').extract()
            yield item