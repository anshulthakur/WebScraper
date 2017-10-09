## Record of things (Unsorted)

So, we want to make a general purpose spider. But first, let's make some specific ones.
These spiders must be able to parse and process javascript also, something that is
inherently missing in scrapy out of the box. For that, we will use `splash` integration
with scrapy in the form of the `scrapy_splash` plugin.

For our first experiment, we want to scrape data off the NSE market website.

References:

1. [Scrapy Tutorial](https://docs.scrapy.org/en/latest/intro/tutorial.html)
2. [Scrapy Splash README](https://github.com/scrapy-plugins/scrapy-splash)
3. [Splash Arguments Lists](http://splash.readthedocs.io/en/stable/api.html)
4. [Docker installation](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-using-the-repository)
5. [Scrapy Project settings](https://stackoverflow.com/questions/14075941/how-to-access-scrapy-settings-from-item-pipeline)

* Install Docker[Docker installation]

```
sudo apt-get remove docker docker-engine docker.io
sudo apt-get update
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get update
sudo apt-get install docker-ce
sudo docker run hello-world
```

* Setup and run a Splash Docker image

```
sudo docker run -p 8050:8050 -p 5023:5023 scrapinghub/splash
```

This docker image may sometimes not have access to the internet. As in my case. In that case, one may use the 
`--net=host` option in it. That should fix things up. Plus, we may need a bigger timeout. So, use `--max-timeout 3600` for setting the timeout to 3600 seconds.

```
sudo docker run -p 8050:8050 -p 5023:5023 --net=host scrapinghub/splash --max-timeout 3600
```

Accessing `localhost:8050` should open a Splash page that allows to scrape some pages. Click on render and it should render the `google.com` page. If not, something is wrong.

* Start a scrapy project:
 
```
scrapy startproject stocks
```

* Setup Scrapy to use Splash by uncommenting or adding these entries in `settings.py` of the project (scrapy_splash related entries need to be added. Others might be there in commented form):

```
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    'stocks.middlewares.StocksSpiderMiddleware': 543,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware':723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

SPLASH_URL = 'http://localhost:8050'

DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'

SPLASH_COOKIES_DEBUG = False #Enable debugging cookies in SplashCookiesMiddleware
SPLASH_LOG_400 = True #Log all 400 errors from Splash
```

* Create a spider by the name NSE in the folder spiders (`nse.py`)

```
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
                            'timeout' : 120,
                          },
                          endpoint = 'render.html', #optional; could be render.json, render.png
                          slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN, #optional
                          )

  def parse(self, response):
    page = response.url
    filename = 'nsepage.html'
    with open(filename, 'wb') as f:
      f.write(response.body)
    self.log("Saved file %s" %filename)
```

Note that we might want to use some settings defined in our settings.py. For that, refer to [Scrapy Project settings].

* Run the spider

```
scrapy crawl nse
```

This should create a file `nsepage.html` containing both static and js rendered content.

### Crawling all pages on a website
* We want to crawl all pages on a web domain (to check for 404 errors).
* Don't want to re-crawl same URLs. (Scrapy takes care of that)
