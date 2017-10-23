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
* We want to avoid some pages (like the login pages. Avoid URLs that have same base URL but different GET parameters, like social media share buttons.) While we would want these rules to be fairly generic, we would also like them to have some element of self-learning and adaptiveness.

```
scrapy crawl general -o ab_url_list.csv
```

**Politeness**
I saw that scrapy's crawl caused masive hits on my analytics page. That means that the analytics API identifies my crawler as a user and not a bot. I would not want that. So, let's delve a little into the politeness of a scraper and how to identify it as a bot.
[Res1](https://blog.scrapinghub.com/2016/08/25/how-to-crawl-the-web-politely-with-scrapy/)

What I already know:
- Obey robots.txt
- Do not scrape too fast to cause either blocking of own IP or damaging the response time of the target site. Crawl slowly.

Changes:
- Set a UserAgent to identify the bot.
- Set DOWNLOAD_DELAY to 1(second) (Instead, set it in the spider class as `download_delay`)
- Enable autothrottle
- Enable HTTPCACHE during development

### More generic nature: Take URL name from CLI

Okay, I've done this part before. I want to pass the name of the URL from the user at runtime rather than having it put in the script. Let's re-do that part.

__Regarding the filters__
It would be better if scrapy itself did the filtering in the link extractors. That can be done if the rules are initialized when the spider is initialized. Modifying our init function may just help that.

Nope, it does not work out of the box. Using the Rule during init does not work.


**When taking the URLs from command line, how do we save the output into a file?**
Using Feed Exporters. For now, the refular ones will work. We will use [CSV](https://doc.scrapy.org/en/latest/topics/feed-exports.html#topics-feed-exports)
Use the `FEED_URI` setting:

```
FEED_URI='ab_list_url.csv'
FEED_FORMAT='csv'
```
> Note that FEED_URI as `FEED_URI='file://ab_list_url.csv'` does not work properly.

**Now, what if we want to have a different list for each domain?**
Clearly, a global setting would not be good for that. In that case, we probably start using the Pipeline and Item Exporters directly.


### For stocks
I want to download the list of all the stocks listed in the market, and then, download all historical data that is currently available. This shouldn't require Scraping but some lightweight scripting.

NSE has less number of shares. So, I'll go with BSE data.

But if it does not allow some API access, then I'll either need to employ Selenium, or via Scrapy-Splash only.

So far, we've created a Selenium script to download historical data and it works fairly fine. Here are the key tweaks:

- Generic Nature had to be forfeit to get more particular results: 
  - Search Fields explicitly by ID
  - The 'To' Date Field does not allow keyboard input. So, we could either mimick the opening of the calendar and select the appropriate date, which could be done, or just go in with the default date (which is of the current day). I went with the latter as I hope to complete the entire pull in a single sitting.
- The BSE site sometimes returned a `503 Internal Error` message on proper pages. This might be because it does not want me to access the site in an automated manner. So, we wrote an `if-else` block to retry the page if such error happened.

Few things not yet known:
- Threads in Python.
- New tabs via selenium.

### Data Modelling: Linear Regression

Some questions we'd like an answer to:

1. Throw in the trending of all the stocks, what is the performance of clustering? Does it have any semblance to the clustering by industry type?
2. How does the co-variance matrix of the stocks data look like? Can it tell which stocks are closely correlated? Positively Correlated, Negatively Correlated, Independent?
3. Given the daily trading positions of the past 10 years, can a linear regression model predict the next value? If yes, then to what accuracy? What should the features be? Hmm! Take one share. Assume that its position is related to the positions of all other shares in the market. Say, its price is going to be affected by the prices, the volumes traded, the percentage changes (some kind of normalization) of other prices. Similarly, its volume is also going to be affected in a similar manner.
4. Indian Markets also derive influence from markets worldwide. So, how much do we need to factor in their movement and trends to account for local variations?
5. How does crude oil prices affect market?
6. How do warfare in the Middle East, UN and US interventions, China, and North Korea military and diplomatic movements affect our markets?
