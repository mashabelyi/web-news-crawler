from datetime import datetime as dt
from scrapy import Spider, Request
import re
from .utils import *

class CNNSpider(Spider):
    name = 'cnn'
    domain = 'www.cnn.com'
    allowed_domains = ['cnn.com']
    base_url = 'http://www.cnn.com'

    def start_requests(self):
        # return urls for each topic within input date range
        time_range = self.settings.get('WAYBACK_MACHINE_TIME_RANGE')
        dates = self.build_date_urls(time_range[0], time_range[1])

        for d in dates:
            yield Request('{}/{}'.format(self.base_url, d))
            # print('https://www.foxnews.com/{}/{}'.format(t,d))


    def build_date_urls(self, start, end):
        start = int_to_date(start)
        end = int_to_date(end)
        current = start
        urls = []
        while current != end:
            urls.append(date_to_path(current))
            current = next_day(current)
        return urls


    def parse(self, response):
        """
        Receive links to archived articles:
        http://web.archive.org/web/{timestamp}/http://www.cnn.com/{yyyy}/{mm}/{dd}/TOPIC/{article-name}.html
        """
        try:
            url = response.meta['wayback_machine_url']
            
            ## parse out topic, date
            m = re.search('.+\.com\/(\d{4}\/\d{2}\/\d{2})\/([^\/]+)\/.+', url)
            date = tuple(m.group(1).split("/"))
            topic = m.group(2)

            title = response.css("h1.pg-headline::text").extract()[0]
            content = response.css("[itemprop=articleBody] .zn-body__paragraph::text").extract()

            item = {
                'title': title,
                'date': int("".join(date)),
                'content': "\n".join(content),
                'topic': topic,
                'url': url,
                'source': self.domain
            }
            return item
        except:
            pass

