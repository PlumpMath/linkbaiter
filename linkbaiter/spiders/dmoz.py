from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from linkbaiter.items import Website


class DmozSpider(BaseSpider):
    name = "dmoz"
    allowed_domains = ["dmoz.org"]
    start_urls = [
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Books/",
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/",
    ]

    def parse(self, response):
        """
        The lines below is a spider contract. For more info see:
        http://doc.scrapy.org/en/latest/topics/contracts.html

        @url http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/
        @scrapes name
        """
        hxs = HtmlXPathSelector(response)

        # XPath for an item looks like this:
        # //*[@id="bd-cross"]/fieldset[3]/ul/li[1]
        sites = hxs.select('//ul/li')
        items = []

        for site in sites:
            item = Website()
            # item['name'] = site.select('a/text()').extract()
            # item['url'] = site.select('a/@href').extract()
            # item['description'] = site.select('text()').re('-\s([^\n]*?)\\n')
            item['name'] = site.select('a/text()').extract()
            item['url'] = site.select('a/@href').extract()
            # item['description'] = site.select('text()').extract()
            item['description'] = [str.strip() for str in site.select('text()').extract()]
            items.append(item)

        return items
