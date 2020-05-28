import json
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from kingfisher_scrapy.base_spider import ZipSpider
from kingfisher_scrapy.items import File, FileItem
from tests import response_fixture, spider_with_crawler


def test_parse_zipfile():
    spider = spider_with_crawler(spider_class=ZipSpider)

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr('test.json', '{}')

    response = response_fixture(body=io.getvalue())
    generator = spider.parse_zipfile(response, 'release_package')
    item = next(generator)

    assert isinstance(item, File)
    assert item == {
        'file_name': 'test.json',
        'url': 'http://example.com',
        'data': b'{}',
        'data_type': 'release_package',
        'encoding': 'utf-8',
        'post_to_api': True,
    }

    with pytest.raises(StopIteration):
        next(generator)


@pytest.mark.parametrize('sample,len_items', [(None, 20), ('true', 10)])
def test_parse_zipfile_json_lines(sample, len_items):
    spider = spider_with_crawler(spider_class=ZipSpider, sample=sample)

    content = []
    for i in range(1, 21):
        content.append('{"key": %s}\n' % i)

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr('test.json', ''.join(content))

    response = response_fixture(body=io.getvalue())
    generator = spider.parse_zipfile(response, 'release_package', file_format='json_lines')
    items = list(generator)

    assert len(items) == len_items

    for i, item in enumerate(items, 1):
        assert isinstance(item, FileItem)
        assert item == {
            'file_name': 'test.json',
            'url': 'http://example.com',
            'number': i,
            'data': '{"key": %s}\n' % i,
            'data_type': 'release_package',
            'encoding': 'utf-8',
        }


@pytest.mark.parametrize('sample,len_items,len_releases', [(None, 2, 100), ('true', 1, 10)])
def test_parse_zipfile_release_package(sample, len_items, len_releases):
    spider = spider_with_crawler(spider_class=ZipSpider, sample=sample)

    package = {'releases': []}
    for i in range(200):
        package['releases'].append({'key': 'value'})

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr('test.json', json.dumps(package))

    response = response_fixture(body=io.getvalue())
    generator = spider.parse_zipfile(response, 'release_package', file_format='release_package')
    items = list(generator)

    assert len(items) == len_items

    for i, item in enumerate(items, 1):
        assert isinstance(item, FileItem)
        assert len(item) == 6
        assert item['file_name'] == 'test.json'
        assert item['url'] == 'http://example.com'
        assert item['number'] == i
        assert len(json.loads(item['data'])['releases']) == len_releases
        assert item['data_type'] == 'release_package'
        assert item['encoding'] == 'utf-8'
