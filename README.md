# News Archive Sraper

### About

Implementation of a web crawler in python using [Scrapy](https://doc.scrapy.org/en/latest/index.html). Archived content is scraped from [Internet Archive](http://web.archive.org/).

Supported news domains: www.cnn.com, www.foxnews.com (more coming)


### Dependencies

Scrapy
```
pip install scrapy
```


### Usage

```
python run.py --source DOMAIN --start START_DATE --end END_DATE
```
The crawler will scrape news content from the input DOMAIN, fetching content that was pubilshed between START_DATE and END_DATE.
The crawler will create a `data/source` directory in the project root folder and save all scraped data in that directory.

### Configuration
- source (string) must be a supported comain (cnn or foxnews)
- start (int) e.g. 20180803 (August 3, 2018)
- end (int) e.g. 20180804 (August 4, 2018)

### Output

The crawler saves scraped content in [JSON Lines](http://jsonlines.org/) format - one record per line.
Sample article record:
```
{
	"title": "Fighting intensifies in eastern Ukraine", 
	"date": 20170203, 
	"content": "At least four Ukrainian soldiers and one civilian have been killed in the last 24 hours....", 
	"topic": "world", 
	"url": "http://web.archive.org/web/20170403185905/http://www.cnn.com/2017/02/03/world/ukraine-fighting-intensifies/index.html", 
	"source": "www.cnn.com"
}
```