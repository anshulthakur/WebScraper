# -*- coding: utf-8 -*-
import scrapy
import scrapy_splash
from scrapy_splash import SplashRequest
from stocks.items import StocksItem

from scrapy.utils.project import get_project_settings

class NSESpider(scrapy.Spider):
  name = "nse"
  
  def start_requests(self):
    urls = [
            'https://www.nseindia.com/',
            #'http://www.bseindia.com/'
           ]
    for url in urls:
      #yield scrapy.Request(url=url, callback=self.parse)
      yield SplashRequest(url, self.parse, 
                          args= {
                            'wait': 0.5,
                            'timeout' : 120, #Timeout to render (default 30 sec)
                            #'url': Prefilled by plugin
                            #'baseurl': Base HTML content, relative resources on page referenced acc. to this., 
                            #'resource_timeout': #Individual resource request timeout value
                            # 'http_method', 'body', 
                            #'js', 'js_source', 'filters', 'allowed_domains', 'allowed_content_types',
                            #'forbidden_content_types', 'viewport', 'images', 'headers', 'save_args',
                            #'load_args'
                          },
                          endpoint = 'render.html', #optional; could be render.json, render.png
                          #splash_url = SPLASH_URL, #optional; overrides SPLASH_URL
                          slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN, #optional
                          )

  def parse(self, response):
    page = response.url
    filename = 'nsepage.html'
    with open(filename, 'wb') as f:
      f.write(response.body)
    self.log("Saved file %s" %filename)
