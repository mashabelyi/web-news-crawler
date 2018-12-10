# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

# wget "http://web.archive.org/cdx/search/cdx?url=https://www.foxnews.com/politics/2018/08/03*&output=json&fl=timestamp,original,statuscode,digest"

import json
from datetime import datetime as dt
from scrapy import signals
from scrapy import Request
from scrapy.http import Response
from scrapy.exceptions import IgnoreRequest


class UnhandledIgnoreRequest(IgnoreRequest):
    pass

class WaybackMachineMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    ## TEST COLLAPSING
	# wget -O collapsed "http://web.archive.org/cdx/search/cdx?url=https://www.foxnews.com/politics/2018/08/03*&output=json&fl=timestamp,original,statuscode,digest&collapse=timestamp:4"

    cdx_url_template = ('http://web.archive.org/cdx/search/cdx?url={url}'
                    '&matchType=prefix&output=json&fl=timestamp,original,statuscode,digest&collapse=timestamp:6&filter=statuscode:200')
    archived_url_template = 'http://web.archive.org/web/{timestamp}/{original}'

    def __init__(self, crawler):
        self.crawler = crawler

        # read the settings
        self.time_range = crawler.settings.get('WAYBACK_MACHINE_TIME_RANGE')

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        return cls(crawler)
        # s = cls()
        # crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        # return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

        # let any web.archive.org requests pass through
        if request.url.find('http://web.archive.org') == 0:
        	# print("process archive request")
        	# print(request.url)

        	return None

        # otherwise request a CDX listing of available articles
        print("Fetching archives for ")
        print(request.url)

        return self.build_cdx_request(request)

    def build_cdx_request(self, request):
        cdx_url = self.cdx_url_template.format(url=request.url)
        cdx_request = Request(cdx_url)
        cdx_request.meta['original_request'] = request
        cdx_request.meta['wayback_machine_cdx_request'] = True
        return cdx_request

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        meta = request.meta

        # parse CDX requests and schedule future snapshot requests
        if meta.get('wayback_machine_cdx_request'):
        	snapshot_requests = self.build_snapshot_requests(response, meta)
        	print("\nFound {} unique articles in\n{}".format(len(snapshot_requests), request.url))

        	# schedule all of the snapshots
        	for snapshot_request in snapshot_requests:
        		self.crawler.engine.schedule(snapshot_request, spider)

        	# abort this request
        	raise UnhandledIgnoreRequest

        # clean up snapshot responses
        if meta.get('original_request'):
        	return response.replace(url=meta['original_request'].url)


        return response

    def build_snapshot_requests(self, response, meta):
        # parse the CDX snapshot data
        data = json.loads(response.text)
        keys, rows = data[0], data[1:]
        def build_dict(row):
            new_dict = {}
            for i, key in enumerate(keys):
                new_dict[key] = row[i]
            return new_dict
        snapshots = list(map(build_dict, rows))

        uniques = []

        # construct the requests
        snapshot_requests = []
        for snapshot in snapshots:
            # # ignore snapshots outside of the time range
            # if not (self.time_range[0] < int(snapshot['timestamp']) < self.time_range[1]):
            #     continue

            if snapshot["statuscode"] != "200":
            	continue

            # only check article urls
            url = snapshot['original']
            if (url.endswith("print.html") 
            	or url.endswith("amp.html")
            	or not url.endswith(".html")):
            	continue

            # want unique urls
            if snapshot['original'] in uniques:
            	continue

            uniques.append(snapshot['original'])

            # update the url to point to the snapshot
            url = self.archived_url_template.format(**snapshot)
            original_request = meta['original_request']
            snapshot_request = original_request.replace(url=url)

            # attach extension specify metadata to the request
            snapshot_request.meta.update({
                'original_request': original_request,
                'wayback_machine_url': snapshot_request.url,
                'wayback_machine_time': dt.strptime(snapshot['timestamp'], '%Y%m%d%H%M%S'),
            })

            snapshot_requests.append(snapshot_request)

        return snapshot_requests

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
