from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from linkbaiter.items import Website, WebsiteLoader


class BuzzfeedSpider(BaseSpider):
    name = "bf"
    allowed_domains = ["buzzfeed.com"]
    start_urls = [
        "http://www.buzzfeed.com/index.xml"
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        # XPath for an item looks like this:
        # /rss/channel/item[]/title
        #                    /link
        #                    /description
        sites = hxs.select('//channel/item')

        for site in sites:
            il = WebsiteLoader(response=response, selector=site)
            il.add_xpath('name', 'title/text()')
            il.add_xpath('url', 'guid/text()')
            il.add_xpath('description', 'title/text()')
            yield il.load_item()
