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

That done. Now, we want to scale. What we want to do is, move from one website to another after the first one has been completely crawled. But, sometimes, it migght happen that we have to abort crawling midway and aren't quite done. So, how can we resume crawling from the same pages that we left off?

One is to make an entry in DB itself when we are done crawling a page. We are done once all its internal links have been yielded. But, by the time we get to this point, the internal links parsed will themselves have started crawl processes. So, DFS comes to bite us here. We can continue with our existing formulation and put up a field in DB marking the status of the URL. So, the `Listing` is created when we enter parsing it, and it is updated when we exit. Then, next time we start at a place which exists in DB with status set to `pending`. It goes down the rabbit hole and encounters more URLs that it has already seen. If they are marked as parsed, skip, else parse. This seems okay in order to maintain the parent-child relationship here.

Another method would be to only make an entry in DB once we are done parsing. But in that case, we always have to start with the base seed URL because its entry isn't created until we are done.

So, using the first method. We must also check while entering a parsing routine if we've parsed it before. Now, that makes things a bit ugly. We created the first DB object in a pipeline. Here, we are explicitly checking its existence in the parse function. When so much of DB has already entered the parse function, why not just make the entry in this function too? Why keep a pipeline?

The querying of DB and checking for existence is a bit slow. So, we could consider having the entries in memories while the size of DB isn't too large. Of course, this ain't very scalable.

* OK. So, now our parsing works more or less fine. On to the next objective. We want to maintain the strength of association between links. So, `a->b` alone is not enough. We also want to know how many times does `a` link to `b` on the page, and on the overall domain. For now, I'm forgoing the time stamping. But, can't this be computed on the go? We have the many to many table. So, put a condition of field 1 `contains` URL `a` and field 2 `contains` URL `b` and count the results. This does not count multiple occurances on a single page. So, if there was a conversation going on between two peoples, that won't be recorded in this simplified model. So, we could instead use an intermediate table explicitly. And lo! that too is supported in Django. So, we create a linkage table and do things to it.

* The thing is too slow for now. Too many DB queries for each request. What we want to do is speed up the crawling operation a little bit. I have been suggested a few things:
  - Put the DB in tmpfs (on RAM) since read/write to disk is slow. Once done crawling, move it out to disk.
  - Index the URL fields. That is supposed to make queries run fast.
Also, I would want to avoid DB queries as much as possible. So, we could have the lists in memory, but I don't think that is very scalable.

* Further, this is supposed to be a very slow process. So, it could be a cron task, or an init.d task that starts running in the background and keeps running. Over time, it will have gathered a lot of information and we could then start doing something about it.
