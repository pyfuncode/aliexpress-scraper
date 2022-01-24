# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from __future__ import print_function

import os.path
from scrapy.exceptions import DropItem
from shutil import which
import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from itemadapter import ItemAdapter


class AmazonPipeline(object):
    SCOPE = ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive']

    def __init__(self, sheet_id, header, spread_sheet):
        self.sheet_id = sheet_id
        self.spread_sheet = spread_sheet
        self.header = header
        self.worksheet = None
        self.token_path = './token.json'
        self.cred_path = './creds.json'
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            sheet_id=crawler.settings.get('GOOGLE_SHEET_ID'),
            spread_sheet=crawler.settings.get('SPREAD_SHEET_NAME'),
            header=crawler.settings.get('FEED_EXPORT_FIELDS')
        )

    def open_spider(self, spider):
        creds = None
        print(self.token_path)
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPE)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.cred_path, scopes=self.SCOPE)
                creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        client = gspread.authorize(credentials=creds)
        sheet = client.open(self.spread_sheet)
        self.worksheet = sheet.get_worksheet_by_id(self.sheet_id)
        is_header =self.worksheet.get('A1')
        if not is_header:
            self.worksheet.insert_row(self.header, index=1)
    def close_spider(self, spider):
        pass

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
