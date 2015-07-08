'''
Created on 06-Jul-2015

@author: anshul
'''
import sys
import os

path = os.path.dirname(os.path.abspath('__file__'))
sys.path.append(path)

import scrapy
from scrapy.crawler import CrawlerProcess

from scrapy.utils.project import get_project_settings

from tutorial.spiders.general import GeneralSpider

#process = CrawlerProcess({
#        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1'
#    })

process = CrawlerProcess(get_project_settings())

process.crawl('General Spider', urls=['http://piratelearner.com'])
process.start()