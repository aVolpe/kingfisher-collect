"""
This spider deliberately generates HTTP errors. You can use this to test whether errors are recorded properly.
"""
import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class TestFail(BaseSpider):
    name = "test_fail"
    start_urls = ['https://www.open-contracting.org']

    def start_requests(self):
        # Fine
        yield scrapy.Request(
            url='https://raw.githubusercontent.com/open-contracting/sample-data/master/fictional-example/1.1/ocds-213czf-000-00001-01-planning.json',  # noqa: E501
            meta={'kf_filename': 'fine.json'}
        )
        # A straight 404
        yield scrapy.Request(
            url='https://www.open-contracting.org/i-want-a-kitten',
            meta={'kf_filename': 'http-404.json'}
        )
        # I broke the server ....
        yield scrapy.Request(
            url='http://httpstat.us/500',
            meta={'kf_filename': 'http-500.json'}
        )
        # .... but actually, yes, I also broke the Proxy too
        yield scrapy.Request(
            url='http://httpstat.us/502',
            meta={'kf_filename': 'http-502.json'}
        )

    def parse(self, response):
        if response.status == 200:
            yield self.build_file_from_response(response, response.request.meta['kf_filename'],
                                                data_type='release_package')

        else:

            yield self.build_file_error_from_response(response)
