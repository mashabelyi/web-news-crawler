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

    def parse2(self, response, url):
        ## parse for older versions of fox
        try:
            title = response.css('.main h1::text').extract()[0]
            content = response.css('.article-text p::text').extract()
            return title, content, None
        except Exception as e:

            # self.logger.warning("error parsing url " + url)
            # self.logger.warning(e)
            return None, None, e

    def parse1(self, response, url):
        try:
            title = response.css("h1.headline::text").extract()[0]
            content = response.css('.article-body p::text').extract()
            return title, content, None

        except Exception as e:
            # self.logger.warning("error parsing url " + url)
            # self.logger.warning(e)
            return None, None, e

    def parse(self, response):
        """
        Receive links to archived articles:
        http://web.archive.org/web/{timestamp}/http://www.foxnews.com/politics/{yyyy}/{mm}/{dd}/{article-name}.html
        """
        url = response.meta['wayback_machine_url']
        title = None
        content = None

        # if url.find('www.foxnews.com:80') >=0:
        #     self.logger.warning("skipping url: " + url)
        #     return None


        try:
            ## parse out topic, date
            m = re.search('.+\/([^\/]+)\/(\d{4}\/\d{2}\/\d{2})\/.+', url)
            topic = m.group(1)
            date = tuple(m.group(2).split("/"))

            title, content, err = self.parse1(response, url)
            if title is None:
                title, content, err = self.parse2(response, url)

            if title is not None:

                item = {
                    'title': title,
                    'date': int("".join(date)),
                    'content': "\n".join(content),
                    'topic': topic,
                    'url': url,
                    'source': self.domain
                }
                return item

            else:
                self.logger.warning("could not parse url " + url)
                self.logger.warning(err)


        except Exception as e:
            self.logger.warning("error parsing url " + url)
            self.logger.warning(e)
            pass

