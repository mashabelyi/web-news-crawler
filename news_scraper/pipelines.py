# -*- coding: utf-8 -*-
import os, json
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class NewsScraperPipeline(object):

	def open_spider(self, spider):
		## make spider dir if not exists
		self.dir = "data/" + spider.name
		if not os.path.exists(self.dir):
			os.makedirs(self.dir)

	def process_item(self, item, spider):
		filename = str(item['date'])

		## subdirectory for scraped year
		subdir = "{}/{}".format(self.dir, filename[0:4])
		if not os.path.exists(subdir):
			os.makedirs(subdir)

		path = "{}/{}.jl".format(subdir, filename)
		f = open(path, 'a')
		f.write(json.dumps(dict(item)) + "\n")
		f.close()
		return item
