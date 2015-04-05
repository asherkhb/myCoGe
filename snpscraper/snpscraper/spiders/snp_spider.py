import scrapy

from snpscraper.items import SnpSet

class SnpSpider(scrapy.Spider):
    name = 'snp'
    allowed_domains = ['pgp-hms.org']
    start_urls = ['https://my.pgp-hms.org/public_genetic_data?utf8=%E2%9C%93&data_type=23andMe&commit=Search']

    def parse(self, response):
        for sel in response.xpath('//div[@class="profile-data"]//tr'):
            item = SnpSet()

            huid = sel.xpath('td[@data-summarize-as="participant"]/a/text()').extract()
            try:
                huid = huid[0].encode('utf-8')
                item['huid'] = huid
            except IndexError:
                #pass
                item['huid'] = sel.xpath('td[@data-summarize-as="participant"]/a/text()').extract()

            download_link = sel.xpath('td[@data-summarize-as="size"]/a/@href').extract()
            try:
                download_link = download_link[0].encode('utf-8')
                item['download_link'] = 'https://my.pgp-hms.org%s' % download_link
            except IndexError:
                #pass
                item['download_link'] = download_link

            profile_link = sel.xpath('td[@data-summarize-as="participant"]/a/@href').extract()
            try:
                profile_link = profile_link[0].encode('utf-8')
                item['profile_link'] = 'https://my.pgp-hms.org%s' % profile_link
                profile_link = 'https://my.pgp-hms.org%s' % profile_link
                request = scrapy.Request(profile_link, callback=self.parse_health)
                request.meta['health'] = item
                yield request

            except IndexError:
                #pass
                item['profile_link'] = profile_link
                item['health'] = ''

            yield item

    def parse_health(self, response):
        item = response.meta['health']
        item['health'] = response.xpath('//div[@class="phr"]').extract()
        return item