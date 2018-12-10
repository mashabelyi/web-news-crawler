import argparse
import scrapy
from scrapy.crawler import CrawlerProcess
from news_scraper.spiders.foxnews_spider import FoxnewsSpider
from news_scraper.spiders.cnn_spider import CNNSpider
from scrapy.utils.project import get_project_settings


def main():
	parser = argparse.ArgumentParser(description='News parse configuration arguments')

	parser.add_argument('--source', type=str, 
    	required=True, help='news source to scrape')
	parser.add_argument('--start', type=int, 
    	required=True, help='scraping start date')
	parser.add_argument('--end', type=int, 
    	required=True, help='scraping end date')
	args = parser.parse_args()

	settings = get_project_settings()
	settings.set('WAYBACK_MACHINE_TIME_RANGE', (args.start, args.end))
	
	process = CrawlerProcess(settings)

	if args.source == 'cnn':
		process.crawl(CNNSpider)
	elif args.source == 'foxnews':
		process.crawl(FoxnewsSpider)
	else:
		print("Unsupported source " + args.source)
		return

	process.start() # the script will block here until the crawling is finished

if __name__ == '__main__':
	main()