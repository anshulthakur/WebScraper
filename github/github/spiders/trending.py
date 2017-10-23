# -*- coding: utf-8 -*-
import scrapy
from github.items import GithubItem

class TrendingSpider(scrapy.Spider):
  name = 'trending'
  allowed_domains = ['github.com']
  start_urls = ['http://github.com/trending']
  # start_requests method can be used in place of start_urls
  # to generate starting URLs dynamically
  #start_requests = 

  def parse(self, response):
    repos = response.selector.css('ol.repo-list li')
    for repo in repos:
      name = repo.xpath('.//h3/a/@href').extract_first()
      lang = repo.css('span[itemprop="programmingLanguage"]::text').extract()
      stars = repo.css('a[href$="stargazers"]::text').extract()
      forks = repo.css('a[href$="network"]::text').extract()

      yield GithubItem(
        repo=name,
        language=lang,
        stars=stars,
        forks=forks,
        )
