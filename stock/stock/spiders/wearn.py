# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import re
import csv
import scrapy
import sqlite3


class WearnSpider(scrapy.Spider):
    name = 'wearn'
    # a50:外資、b50:投信
    start_urls = ['https://stock.wearn.com/a50.asp',
                  'https://stock.wearn.com/b50.asp']

    def start_requests(self):
        for url in self.start_urls:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/51.0.2704.84 Safari/537.36',
            }

            meta = {'dont_redirect': True, "handle_httpstatus_list": [302]}

            yield scrapy.Request(
                url,
                headers=headers,
                meta=meta
            )

    def parse(self, response):
        title = response.css('.stockfundthree > h3::text').get()
        day = re.search(r'\d+', title).group()

        today = datetime.today()  # + timedelta(hours=8)

        if not today.day == day:
            return

        page_name = response.url.split(r'/')[-1]
        all_row = response.css('.stockfundthreecon tr')

        today -= timedelta(hours=today.hour,
                           minutes=today.minute,
                           seconds=today.second,
                           microseconds=today.microsecond)

        data = {
            'number': all_row.xpath('td[2]/text()').getall(),
            'name': all_row.xpath('td[3]//a/text()').getall(),
            'buy': all_row.xpath('td[4]/text()').getall(),
            'sell': all_row.xpath('td[5]/text()').getall(),
            'diff': all_row.xpath('td[6]/text()').getall()
        }

        table_name = 'finder_foreign' if page_name == 'a50.asp' else 'finder_investment'
        a = set(zip(*data.values()))
        a = [(today,) + i for i in a]

        conn = sqlite3.connect(
            '../../db.sqlite3',
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        c = conn.cursor()

        c.executemany(
            f'INSERT INTO {table_name} (datetime, number, name, buy, sell, diff) VALUES (?,?,?,?,?,?)',
            a
        )

        conn.commit()
        conn.close()

        # with open(f'csv/{day}_{page_name}.csv', 'w', newline='', encoding='UTF-8') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(data.keys())
        #     for i in a:
        #         writer.writerow(i)
