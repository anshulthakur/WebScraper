'''
Created on 12-Oct-2017

@author: anshul
'''
import sys
import os

path = os.path.dirname(os.path.abspath('__file__'))
sys.path.append(path)

from scrapy.crawler import CrawlerProcess

from scrapy.utils.project import get_project_settings


#===================================
# Class Declarations
#===================================
class InputError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return str(self.msg)

#===================================
# Main script
#===================================
urls = []
   
if len(sys.argv) < 2:
    raise InputError('At least one URL must be provided for crawler')

for i in range(1, len(sys.argv)):
    print sys.argv[i]
    urls.append(sys.argv[i])

#Crawl the given set of URLs
#NOT validating the URLs here. The URLParse method would implicitly do that.
process = CrawlerProcess(get_project_settings())
process.crawl('general', urls=urls)
process.start()
