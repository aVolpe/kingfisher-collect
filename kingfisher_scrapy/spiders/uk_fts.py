import scrapy

from kingfisher_scrapy.base_spider import LinksSpider


class UKContractsFinder(LinksSpider):
    name = 'uk_fts'

    def start_requests(self):
        yield scrapy.Request(
            # This URL was provided by the publisher and is not the production URL.
            url='https://enoticetest.service.xgov.uk/api/1.0/ocdsReleasePackages',
            meta={'kf_filename': 'start.json'},
            headers={'Accept': 'application/json'},
        )

    def parse(self, response):
        yield from self.parse_next_link(response, 'release_package_in_ocdsReleasePackage_in_list_in_results')
