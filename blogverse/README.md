## Readme

This project has a few small aims.

### Pass 1
1. Given a URL, it crawls the domain from there and lists all the URLs to a file (for now).
2. It then parses all the URLs and finds links to all external URLs placed on the site.
3. It then crawls those domains completely and finds more URLs.

In this way, it creates a web of URLs.

### Pass 2
**Some (assumed) properties of content pages**
- URLs to other places are not too frequent in the main content.
- Where used (by the author as attribution or by commentors as backlinks), these are accompanied by a text block.
- Closely placed URLs and too little text content indicates sidebar like information where either affiliate information is kept, or archival info.
- URL to content page would be found on aggregation pages <=> aggregation pages contain URLs to self domain.
- Affiliate links and other layouts are liekly to get repeated over the content page as well as aggregate page.
- External links of main interest would be the other URLs that are not common between aggregate page and content page.
- Blog pages will have less textual information outside one main container. For other kinds of websites, there'll be greater amount of text spread out in other places/blocks too. Text density helps classify site as content site/consumer site.

1. Classify page as content page or aggregate page and create a list of Content URLs on the domain.
2. Parse all content pages and find non-affiliate links to external URLs and make a list of those.
3. Do the same for those URLs also.


### Implementation and running

```
python runner.py <domain url>
```

This crawls all the URLs on a domain whether or not they belong to that domain.
Also, creates an entry to those domains and URLs in the DB

* How do we make sure that Scrapy does not scrape the URLs that it has already seen. We don't want to pass them to Scrapy even when it filters duplicates. For spanning a crawl across multiple sessions, we'll use Scrapy's persistence feature. That allows pausing. But when does Scrapy stop? So, it will probably go on crawling unless our parse function gives up. So, our yield has to stop. This can be done if we don't find any new URL. 

This calls for querying from right inside the spider code, something I was trying to avoid (and hence, using pipeline). Anyhow!
