# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from __future__ import print_function

import os.path

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class AliexpressPipeline(object):
    SCOPE = ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive']

    def __init__(self, sheet_index, header, spread_sheet_url):
        self.sheet_index = sheet_index
        self.spread_sheet_url = spread_sheet_url
        self.header = header
        self.worksheet = None
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.cred_path = os.path.join(ROOT_DIR, 'creds.json')
        self.token = os.path.join(ROOT_DIR, 'token.json')

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(
            sheet_index=settings.get('GOOGLE_SHEET_INDEX'),
            spread_sheet_url=settings.get('SPREAD_SHEET_URL'),
            header=settings.get('FEED_EXPORT_FIELDS')
        )

    def open_spider(self, spider):
        creds = None
        if os.path.exists(self.token):
            creds = Credentials.from_authorized_user_file(self.token, self.SCOPE)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.cred_path, scopes=self.SCOPE)
                creds = flow.run_local_server(port=0)
            with open(self.token, 'w') as token:
                token.write(creds.to_json())
        client = gspread.authorize(credentials=creds)

        sheet = client.open_by_url(self.spread_sheet_url)
        self.worksheet = sheet.get_worksheet(self.sheet_index)
        is_header = self.worksheet.get('A1')
        if not is_header:
            self.worksheet.insert_row(self.header, index=1)

    def process_item(self, item, spider):
        self.worksheet.append_row(
            [
                item['Category'],
                item['Sub Category'],
                item['3rd Category'],
                item['Product Model'],
                item['Product Name'],
                item['hk_intl_price'],
                item['hk_intl stock status'],
                item['Products Shipping Weight(g)'],
                item['Quantity'],
                item['Description'],
                item['Products Specifications'],
                item['Products Package Includes'],
                item['Images Url'],
            ]
        )
        return item

    def close_spider(self, spider):
        pass


class DuplicatesPipeline:

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['Color'] in self.ids_seen:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.ids_seen.add(adapter['id'])
            return item
