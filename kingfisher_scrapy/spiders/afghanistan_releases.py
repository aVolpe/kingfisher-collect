import json
import time

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class AfghanistanReleases(BaseSpider):
    name = 'afghanistan_releases'
    start_urls = ['https://ocds.ageops.net/api/ocds/releases/dates']
    download_delay = 1.5

    def start_requests(self):
        yield scrapy.Request(
            url='https://ocds.ageops.net/api/ocds/releases/dates',
            callback=self.parse_list
        )

    def parse_list(self, response):
        if response.status == 200:

            files_urls = json.loads(response.text)
            if self.sample:
                files_urls = [files_urls[0]]

            for file_url in files_urls:
                yield scrapy.Request(
                    url=file_url,
                    meta={'kf_filename': file_url.split('/')[-1]+'.json'},
                    callback=self.parse_release_list
                )
        else:
            yield self.build_file_error_from_response(response, filename='list.json')

    def parse_release_list(self, response):
        if response.status == 200:

            files_urls = json.loads(response.text)
            if self.sample:
                files_urls = [files_urls[0]]

            for file_url in files_urls:
                yield scrapy.Request(
                    url=file_url,
                    meta={'kf_filename': file_url.split('/')[-1] + '.json'},
                    callback=self.parse_release
                )
        elif response.status == 429:
            self.crawler.engine.pause()
            time.sleep(600)  # 10 minutes
            self.crawler.engine.unpause()
            url = response.request.url
            # This is dangerous as we might get stuck in a loop here if we always get a 429 response. Try this for now.
            yield scrapy.Request(
                url=url,
                meta={'kf_filename': url.split('/')[-1] + '.json'},
                callback=self.parse_release_list,
                dont_filter=True,
            )
        else:
            yield self.build_file_error_from_response(response)

    def parse_release(self, response):
        if response.status == 200:

            yield self.build_file_from_response(response, response.request.meta['kf_filename'], data_type="release")

        elif response.status == 429:
            self.crawler.engine.pause()
            time.sleep(600)  # 10 minutes
            self.crawler.engine.unpause()
            url = response.request.url
            # This is dangerous as we might get stuck in a loop here if we always get a 429 response. Try this for now.
            yield scrapy.Request(
                url=url,
                meta={'kf_filename': url.split('/')[-1] + '.json'},
                callback=self.parse_release,
                dont_filter=True,
            )
        else:
            yield self.build_file_error_from_response(response)
