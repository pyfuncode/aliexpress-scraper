import json
import re
import time

import requests
import scrapy
from scrapy.selector import Selector
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..utils import (get_random_agent,
                     find_categories, image_html, restore_cookies,
                     spect_table,
                     sku_color_size_list,
                     key_exists,
                     cookie_parser,
                     remove_tag,
                     check_model,
                     find_package_detail,
                     )


class AmazonSearchSpider(scrapy.Spider):
    name = 'category'
    allowed_domains = ['www.aliexpress.com']
    page = 1

    def __init__(self, keyword, is_single=0, *args, **kwargs):
        self.keyword = keyword
        self.is_single = is_single
        self.request = requests.session()

    def start_requests(self):

        if self.keyword.startswith('https:'):
            url = self.keyword
        else:
            url = f'https://www.aliexpress.com/wholesale?catId=0&SearchText={self.keyword}'

        if self.is_single:
            yield scrapy.Request(
                url=url,
                headers={
                    'user-agent': get_random_agent(),
                    'referer': 'https://www.aliexpress.com',
                },
                cookies=cookie_parser(),
                callback=self.parse_product,

            )
        else:
            yield SeleniumRequest(

                url=url,
                headers={
                    'user-agent': get_random_agent(),
                    'referer': 'https://www.aliexpress.com',

                },
                callback=self.parse,

            )

    def parse(self, response, **kwargs):
        driver = response.meta['driver']
        try:
            WebDriverWait(driver, 120).until(
                lambda driver: driver.find_element(By.CLASS_NAME, 'JIIxO'))
        except:
            pass

        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));")
        time.sleep(2)
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight*3/4.3));")
        time.sleep(2)

        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight));")
        time.sleep(2)
        try:
            driver.execute_script(
                'document.getElementsByClassName("next-next")[0].scrollIntoView(true);')
            time.sleep(2)
        except:
            pass
        self.request, cookies = restore_cookies(
            driver=driver, request=self.request)
        resp = Selector(text=driver.page_source)
        p_urls = resp.css('div.product-container div.JIIxO a[title]')
        p_urls_two = resp.xpath(
            '//div[@class="product-container"]/div[@class="JIIxO"]/a')
        products_urls = p_urls if p_urls else p_urls_two
        for product in products_urls:
            link = product.attrib['href']
            first_part = link.split('.html')[0]
            product_id = first_part.split('item/')[1]
            yield response.follow(
                url=link,
                callback=self.parse_product,
                headers={
                    'user-agent': get_random_agent(),
                    'referer': response.url,

                },
                cookies=cookies,
                meta={'id': product_id}
            )

        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "next-next")))
        except:
            element = None
            pass

        if element and element.is_enabled():

            self.page += 1
            if self.keyword.startswith('https:'):
                current_url = driver.current_url
                sub_url = re.sub(f'&page=[0-9]?[0-9]', '', current_url)
                url = f'{sub_url}&page={self.page}'

            else:
                url = f'https://www.aliexpress.com/wholesale?catId=0&SearchText={self.keyword}&page={self.page}'
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                headers={
                    'user-agent': get_random_agent(),
                    'referer': 'https://www.aliexpress.com'

                },
                method='GET'
            )

    def parse_product(self, response):
        matches = ["pcs", "1/2 pcs", "2 pcs"]  #
        pattren = re.compile(
            r'\bdata\s*:\s*(\{.*?\})\s*;\s*', re.MULTILINE | re.DOTALL)
        json_data = response.css('script::text').re_first(pattren)
        json_obj_pattren = re.compile(
            r'(\{.*?\})\s*,\s*csrf', re.MULTILINE | re.DOTALL)
        js = json_obj_pattren.findall(json_data)[0]
        try:
            product_detail = json.loads(js)
        except:
            return None
        product_id = product_detail.get('actionModule').get('productId')

        breadcumb = product_detail.get(
            'crossLinkModule').get('breadCrumbPathList', None)
        categories = find_categories(breadcumb)
        category = categories.get('cat', None)
        subcategory = categories.get('sub', None)
        supercategory = categories.get('sup', None)
        quantity = product_detail.get(
            'quantityModule').get('totalAvailQuantity')
        image = product_detail.get('imageModule').get('imagePathList')
        # package Info
        sku_request = self.request.get(
            url=f'https://m.aliexpress.com/fn/fc-detail-msite/index?productId={product_id}&pageName=detail-msite',
            headers={
                'user-agent': 'Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36'
            }
        )
        price = product_detail.get('priceModule').get(
            'maxActivityAmount').get('value')
        title = None
        if sku_request.status_code == 200:
            data = sku_request.json()

            product = data.get('data').get('data')
            package_details = product.get(key_exists(
                product, 'freight_1663', 'freight')).get('fields').get('packageInfo')
            # price = product.get(key_exists(product, 'price_1649', 'price')).get(
            # 'fields').get('maxPrice')
            title = product_detail.get('pageModule').get('title')
            if any(x in title.lower() for x in matches):
                return None
            weight = package_details.get('weight', None)
            height_cm = package_details.get('height', None)
            width_cm = package_details.get('width', None)
            length_cm = package_details.get('length', None)
            dimentions = '({} X {} X {})cm (L x W x H)'.format(
                length_cm, width_cm, height_cm)
        else:
            weight = None
            height_cm = None
            length_cm = None
            width_cm = None
            dimentions = None

        product_weight = float(weight) * 1000

        specs = product_detail.get('specsModule').get('props')
        sku_properties = product_detail.get(
            'skuModule').get('productSKUPropertyList')
        sku_color_list, sku_size_list = sku_color_size_list(sku_properties)

        specs_dict = {x.get('attrName'): x.get('attrValue')
                      for x in specs if x is not None}
        if weight:
            specs_dict.update({'Weight': f'{float(weight) * 1000} (g)'})
        if dimentions:
            specs_dict.update({'Dimensions': dimentions})
        if len(sku_color_list) > 0:
            specs_dict.update({'Color': sku_color_list[0]})
        if len(sku_size_list) > 0:
            specs_dict.update({'Size': sku_size_list[0]})
        specification = spect_table(specs_dict)
        product_mode = str(check_model(specs_dict))
        desription = product_detail.get(
            'descriptionModule').get('descriptionUrl')
        des_response = self.request.get(url=desription)
        des_selector = scrapy.selector.Selector(text=des_response.text)
        description_list = des_selector.xpath(
            '//p/text() | //div/descendant::*/text() | //span/descendant::*/text() |//li/descendant::*/text()').getall()

        text_descrtipion = ' '.join(list(map(remove_tag, description_list)))
        description_img = des_selector.xpath('//img/@src').getall()

        img_list = '\n'.join(image_html(
            map(remove_tag, description_img), title))
        desc = text_descrtipion.rstrip() + img_list.replace("\"\"", "\"")
        packge_d = find_package_detail(description_list)
        if packge_d:
            packge_include = '<b>{}</b>\n{}'.format(title, packge_d)
        else:
            packge_include = None

        stock = 'In Stock' if quantity > 0 else 'Sold out'
        yield {

            'Category': remove_tag(category),
            'Sub Category': remove_tag(subcategory),
            '3rd Category': remove_tag(supercategory),
            'Product Model': remove_tag(product_mode),
            'Product Name': remove_tag(title),
            'hk_intl_price': price,
            'hk_intl stock status': stock,
            'Products Shipping Weight(g)': product_weight,
            'Quantity': quantity,
            'Description': '',
            'Products Specifications': specification,
            'Products Package Includes': packge_include,
            'Images Url': '\n'.join(image), }
