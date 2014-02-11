from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from linkbaiter.items import Website, WebsiteLoader


class BusinessInspider(BaseSpider):
    name = "bi"
    allowed_domains = ["businessinsider.com"]
    start_urls = [
        # "http://localhost:8000/bi-2014.02.xml"
        # "http://localhost:8000/bi-2014.02-short.xml"
        "http://feeds.feedburner.com/businessinsider?format=xml"
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        # XPath for an item looks like this:
        # /rss/channel/item[]/title
        #                    /link
        #                    /description
        sites = hxs.select('//channel/item')
        #items = []

        for site in sites:
            #item = Website()
            #item['name'] = site.select('title/text()').extract()
            #item['url'] = site.select('guid/text()').extract()
            #item['description'] = "" # [str.strip() for str in site.select('description/text()').extract()]
            #items.append(item)

            il = WebsiteLoader(response=response, selector=site)
            il.add_xpath('name', 'title/text()')
            il.add_xpath('url', 'guid/text()')
            il.add_xpath('description', 'title/text()')
            yield il.load_item()


        #return items
