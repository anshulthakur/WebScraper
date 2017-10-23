# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class GithubPipeline(object):
    def process_item(self, item, spider):
        item['language'] = ''.join(item['language']).strip()
        item['stars'] = ''.join(item['stars']).strip()
        item['forks'] = ''.join(item['forks']).strip()
        return item
