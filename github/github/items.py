# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GithubItem(scrapy.Item):
    # define the fields for your item here like:
    repo = scrapy.Field()
    language = scrapy.Field()
    stars = scrapy.Field()
    forks = scrapy.Field()
    
