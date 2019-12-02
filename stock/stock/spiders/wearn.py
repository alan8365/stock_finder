# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import re
import csv
import scrapy
import sqlite3
import psycopg2

DATABASE_URL = 'postgres://plkrpgvahxvvko:f06c3423496c41a704b193effc37298fc891dbb2ae4944478d26d063ece73ae0@ec2-50-17-231-192.compute-1.amazonaws.com:5432/dail56rnv3mqlr'


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
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()

        title = response.css('.stockfundthree > h3::text').get()
        day = int(re.search(r'\d+', title).group())

        page_name = response.url.split(r'/')[-1]
        table_name = 'finder_foreign' if page_name == 'a50.asp' else 'finder_investment'

        c.execute(f'SELECT max(datetime) FROM {table_name}')
        last_day, = c.fetchone()

        if not last_day:
            last_day = datetime.strptime('2019-01-01', '%Y-%m-%d')
            # last_day = datetime.strptime(last_day, '%Y-%m-%d %H:%M:%S')

        if last_day.day == day:
            print('day exist.')
            return

        trans_day = datetime.strptime(response.headers['Date'].decode(), '%a, %d %b %Y %H:%M:%S %Z')
        trans_day -= timedelta(hours=trans_day.hour,
                               minutes=trans_day.minute,
                               seconds=trans_day.second)

        if trans_day.day != day:
            print('day error')
            return

        all_row = response.css('.stockfundthreecon tr')

        data = {
            'number': all_row.xpath('td[2]/text()').getall(),
            'name': all_row.xpath('td[3]//a/text()').getall(),
            'buy': all_row.xpath('td[4]/text()').getall(),
            'sell': all_row.xpath('td[5]/text()').getall(),
            'diff': all_row.xpath('td[6]/text()').getall()
        }

        a = set(zip(*data.values()))
        a = [(trans_day,) + i for i in a]

        c.executemany(
            f'INSERT INTO {table_name} (datetime, number, name, buy, sell, diff) VALUES (%s,%s,%s,%s,%s,%s)',
            a
        )

        conn.commit()
        conn.close()

        with open(f'csv/{day}_{page_name}.csv', 'w', newline='', encoding='UTF-8') as f:
            writer = csv.writer(f)
            writer.writerow(data.keys())
            for i in a:
                writer.writerow(i)
