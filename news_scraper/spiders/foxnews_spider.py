from scrapy import Spider, Request
import re
from .utils import *

foxnews_topics = ['politics', 'us', 'world', 'opinion', 'entertainment']

class FoxnewsSpider(Spider):
    name = 'foxnews'
    domain = 'www.foxnews.com'
    allowed_domains = ['foxnews.com']
    base_url = 'http://www.foxnews.com'
    # start_urls = [
    #     'https://www.foxnews.com/politics/comey-reveals-he-concealed-trump-meeting-memo-from-doj-leaders'
    # ]

    def start_requests(self):
        # return urls for each topic within input date range
        time_range = self.settings.get('WAYBACK_MACHINE_TIME_RANGE')
        dates = self.build_date_urls(time_range[0], time_range[1])

        for t in foxnews_topics:
            for d in dates:
                yield Request('{}/{}/{}'.format(self.base_url, t,d))
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


    def parse_dummy(self, response):
        # dummy parse

        return ({'timestamp': response.meta['wayback_machine_time'].timestamp(), 
            'url': response.url})

    def parse(self, response):
        """
        Receive links to archived articles:
        http://web.archive.org/web/{timestamp}/http://www.foxnews.com/politics/{yyyy}/{mm}/{dd}/{article-name}.html
        """
        try:
            url = response.meta['wayback_machine_url']
            
            ## parse out topic, date
            topic, date = info_from_url(url)

            ## parse out date from url
            m = re.search('.+(\d{4}\/\d{2}\/\d{2}\/).+', 'abcdef')

            title = response.css("h1.headline::text").extract()[0]
            text = []
            body = response.css('.article-body')
            for p in response.css('.article-body').xpath('p/text()'):
                try:
                    text.append(p.extract())
                except:
                    pass

            timestamp = response.meta['wayback_machine_time'].timestamp()
            item = {
                'title': title,
                'date': int("".join(date)),
                'content': "\n".join(text),
                'topic': topic,
                'url': url,
                'source': self.domain
            }
            return item
        except:
            pass

