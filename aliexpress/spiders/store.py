import json
import re
import time

import requests
import scrapy
from scrapy.selector import Selector
from scrapyselenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..utils import (get_random_agent,
                     find_categories, image_html, json_output,
                     spect_table,
                     sku_color_size_list,
                     key_exists,
                     restore_cookies,
                     remove_tag,
                     check_model,
                     find_package_detail, cleaned_image_description)


class StoreSpider(scrapy.Spider):
    name = 'store'
    allowed_domains = ['www.aliexpress.com']
    # keyword = 'https://www.aliexpress.com/store/4493070?spm=a2g0o.productlist.0.0.18fb4f9bkQ66Cn'
    # keyword = 'https://www.aliexpress.com/store/top-rated-products/3874104.html?spm=a2g0o.detail.1000061.4.7b5a11927qzNTN'

    def __init__(self, keyword, is_single=0, *args, **kwargs):
        self.keyword = keyword
        self.request = requests.session()

    def start_requests(self):
        self.request = requests.session()
        yield SeleniumRequest(
            url=self.keyword,
            headers={
                'user-agent': get_random_agent(),
                'referer': 'https://www.aliexpress.com',
            },
            callback=self.parse,

        )

    def parse(self, response):
        driver = response.meta['driver']
        try:
            WebDriverWait(driver, 10).until(
                lambda driver: driver.find_element(By.CLASS_NAME, 'items-list'))
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
                'document.getElementById("pagination-bottom")[0].scrollIntoView(true);')
            time.sleep(2)
        except:
            pass
        self.request, cookies = restore_cookies(
            driver=driver, request=self.request)
        resp = Selector(text=driver.page_source)

        products = resp.xpath(
            '//a[@ae_button_type="productList_click"]|//div[@ae_button_type="smartJustForYou_click"]| //ul[contains(@class,"items-list")]/li/div[@class="detail"]/h3/a')

        for product in products:
            link = product.xpath('.//@href | .//@data-href').get()
            if link:
                yield response.follow(
                    url=link,
                    callback=self.parse_product,
                    headers={
                        'user-agent': get_random_agent(),
                        'referer': response.url,
                    },
                    cookies=cookies,
                )

        current_url = resp.xpath(
            '//a[@class="ui-pagination-next"]/@href').get()
        print('*************************************Current_URL_LINk*********************', current_url)
        if current_url:
            yield SeleniumRequest(
                url=f'https:{current_url}',
                callback=self.parse,
                headers={
                    'user-agent': get_random_agent(),
                    'referer': response.url

                },
            )

    def parse_product(self, response):
        matches = ["pcs", "1/2 pcs", "2 pcs"]

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
                'user-agent': 'Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36',

            }
        )
        title = None
        if sku_request.status_code == 200:
            data = sku_request.json()
            product = data.get('data').get('data')
            package_details = product.get(key_exists(
                product, 'freight_1663', 'freight')).get('fields').get('packageInfo')
            price = product.get(key_exists(product, 'price_1649', 'price')).get(
                'fields').get('maxPrice')
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
            '//p/descendant-or-self::*/text()| //div/descendant::*/text() | //span/descendant::*/text() |//li/descendant::*/text() | //p/descendant::*/text()').getall()
        text_descrtipion = '\n'.join(list(map(remove_tag, description_list)))
        description_img = des_selector.xpath('//img/@src').getall()

        img_list = '\n'.join(image_html(
            map(remove_tag, description_img), title))
        descrip = text_descrtipion.rstrip()+img_list.replace("\"\"", "\"")
        packge_d = find_package_detail(description_list)
        if packge_d:
            packge_include = '<b>{}</b>\n{}'.format(title, packge_d)
        else:
            packge_include = None
        stock = 'In Stock' if quantity > 0 else 'Sold out'
        yield {

            'Category': category,
            'Sub Category': subcategory,
            '3rd Category': supercategory,
            'Product Model': product_mode,
            'Product Name': title,
            'hk_intl_price': price,
            'hk_intl stock status': stock,
            'Products Shipping Weight(g)': product_weight,
            'Quantity': quantity,
            'Description': descrip,
            'Products Specifications': specification,
            'Products Package Includes': packge_include,
            'Images Url': '\n'.join(image), }
