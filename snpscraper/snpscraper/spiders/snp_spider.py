import scrapy

from snpscraper.items import SnpSet

class SnpSpider(scrapy.Spider):
    name = "snp"
    allowed_domains = ["pgp-hms.org"]
    start_urls = [
        "https://my.pgp-hms.org/public_genetic_data?utf8=%E2%9C%93&data_type=23andMe&commit=Search"
    ]

    def parse(self, response):
        for sel in response.xpath('//div[@class="profile-data"]//tr'):
	    item = SnpSet()
            item['huid'] = sel.xpath('td[@data-summarize-as="participant"]/a/text()').extract()
	    item['link'] = sel.xpath('td[@data-summarize-as="size"]/a/@href').extract()
            yield item
