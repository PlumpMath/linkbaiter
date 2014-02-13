import random
from scrapy.exceptions import IgnoreRequest
import re
from scrapy.exceptions import DropItem
from datetime import datetime
from hashlib import md5
from twisted.enterprise import adbapi
import os

class AlertRegexesPipeline(object):
    """A pipeline for alerting items which match certain regexes in their
    name"""

    # put all words in lowercase
    regex_to_alert = [
        re.compile("^\d{1,} "),
        re.compile("35 Things")
        ]

    def process_item(self, item, spider):
        item_match = False
        for regex in self.regex_to_alert:
            #print("Trying pattern %s with name %s" % (regex.pattern, name))
            if regex.match(unicode(item['name'])):
                item_match = True

        #print("Tried all patterns. Was there a match? %s" % item_match)
        # once the name has been matched against all, and there was a match
        if item_match:
            return item
        else:
            raise DropItem("Didn't match any of the patterns")


class RandomUserAgent(object):
    """Randomly rotate user agents based on a list of predefined ones"""

    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('USER_AGENTS'))

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', random.choice(self.agents))

class MySQLStorePipeline(object):
    """A pipeline to store the item in a MySQL database.

    This implementation uses Twisted's asynchronous database API.
    """

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=os.environ['PLUSONENEWS_MYSQL_HOST'],
            db=os.environ['PLUSONENEWS_MYSQL_DBNAME'],
            user=os.environ['PLUSONENEWS_MYSQL_USER'],
            passwd=os.environ['PLUSONENEWS_MYSQL_PASSWD'],
            charset='utf8',
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        # run db query in the thread pool
        d = self.dbpool.runInteraction(self._do_upsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        # at the end return the item in case of success or failure
        d.addBoth(lambda _: item)
        # return the deferred instead the item. This makes the engine to
        # process next item (according to CONCURRENT_ITEMS setting) after this
        # operation (deferred) has finished.
        return d

    def _do_upsert(self, conn, item, spider):
        """Perform an insert or update."""

        guid = self._get_guid(item)
        now = datetime.utcnow().replace(microsecond=0).isoformat(' ')

        conn.execute("""SELECT EXISTS(
            SELECT 1 FROM website WHERE guid = %s
        )""", (guid, ))
        ret = conn.fetchone()[0]

        if ret:
            conn.execute("""
                UPDATE website
                SET name=%s, description=%s, url=%s, updated=%s
                WHERE guid=%s
            """, (item['name'], item['description'], item['url'], now, guid))
            spider.log("Item updated in db: %s %r" % (guid, item))
        else:
            conn.execute("""
                INSERT INTO website (guid, name, description, url, updated)
                VALUES (%s, %s, %s, %s, %s)
            """, (guid, item['name'], item['description'], item['url'], now))
            spider.log("Item stored in db: %s %r" % (guid, item))

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        log.err(failure)

    def _get_guid(self, item):
        """Generates an unique identifier for a given item."""
        # hash based solely in the url field
        return md5(item['url']).hexdigest()
