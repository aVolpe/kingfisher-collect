import datetime

import scrapy

from kingfisher_scrapy.base_spider import LinksSpider


class Australia(LinksSpider):

    name = 'australia'

    def start_requests(self):

        if self.sample:
            yield scrapy.Request(
                url='https://api.tenders.gov.au/ocds/findByDates/contractPublished/2018-01-01T00:00:00Z/2018-12-31T23'
                    ':59:59Z',
                meta={'kf_filename': 'year-2018.json'}
            )
        else:
            current_year = datetime.datetime.now().year + 1
            for year in range(2004, current_year):
                yield scrapy.Request(
                    url='https://api.tenders.gov.au/ocds/findByDates/contractPublished/'
                        '{}-01-01T00:00:00Z/{}-12-31T23:59:59Z'.format(year, year),
                    meta={'kf_filename': 'year-{}.json'.format(year)}
                )

    def parse(self, response):
        yield from self.parse_next_link(response, 'release_package')
