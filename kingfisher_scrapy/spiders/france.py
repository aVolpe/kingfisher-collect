import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class France(BaseSpider):
    name = "france"

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.data.gouv.fr/api/1/datasets/?organization=534fff75a3a7292c64a77de4',
            callback=self.parse_item
        )

    def parse_item(self, response):
        if response.status == 200:
            json_data = json.loads(response.text)
            data = json_data['data']
            for item in data:
                resources = item['resources']
                for resource in resources:
                    description = resource['description']
                    if description and (description.count("OCDS") or description.count("ocds")):
                        url = resource['url']
                        yield scrapy.Request(
                            url,
                            meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'},
                        )
                        if self.sample:
                            break
                else:
                    continue
                break
            else:
                next_page = json_data.get('next_page')
                if next_page:
                    yield scrapy.Request(
                        next_page,
                        callback=self.parse_item
                    )
        else:
            yield self.build_file_error_from_response(response)

    def parse(self, response):
        if response.status == 200:
            yield self.build_file_from_response(
                response,
                response.request.meta['kf_filename'],
                data_type="release_package"
            )
        else:
            yield self.build_file_error_from_response(response)
