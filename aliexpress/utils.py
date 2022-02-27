import json
import pickle
import re
from http.cookies import SimpleCookie
from pathlib import Path
from random import choice

pack_pattern = pk_inc_pattern = re.compile(
    r'^\n?[1-9]\s*?[×x*]\s*?.*?$', re.MULTILINE | re.DOTALL | re.IGNORECASE)


def find_package_detail(description_cleaned):
    pack_inc_list = pack_pattern.findall('\n'.join(description_cleaned))
    packge_include = None
    if len(pack_inc_list) > 0:
        packge_include = pack_inc(
            pack_inc_list) if len(pack_inc_list) > 0 else None
    return packge_include


def save_cookies(driver):
    if not Path("cookies.pkl").exists():
        with Path("cookies.pkl").open(mode="wb") as c:
            pickle.dump(driver.get_cookies(), c)


def is_cooke_exit():
    return Path("cookies.pkl").exists()


def restore_cookies(driver, request):
    get_saved_cookies = driver.get_cookies()
    for c in get_saved_cookies:
        request.cookies.set(c['name'], c['value'])
    return request, get_saved_cookies


def cookie_parser():
    cookie_string = 'ali_apache_id=11.10.85.103.1636859590869.176732.0; acs_usuc_t=x_csrf=nnrdvo7d4z3t&acs_rt=557e56da2e85497fa4794b3e26d1808e; intl_locale=en_US; xman_t=riN1LRZFbds8dXyMxpt/73tJzhbywZd5bppYzB+EGyUi25ySLdhbXh/sHnuktslj; cna=y2wXGjGU7RoCAScqjE3vJgIh; ali_apache_track=; ali_apache_tracktmp=; _bl_uid=6wkbFvk7y7ennaxh6v5UfRC2Lyze; _gcl_au=1.1.1978596842.1636859596; XSRF-TOKEN=f5780d33-828a-460a-8565-417f4f191246; e_id=pt10; xman_f=1u6xj//depwIgADSyA6Mf17bUVPNDFZmpKukee+8XYPNHnqLn7ORvnp6DaV7kF4UkjBSm+3vsIgd+NUPmwQXyj+IrQowyugExikYIlx3jXzewKfcR7PY/Q==; _mle_tmp_enc0=Ey%2Fp8LswzxA3J47VsqxI%2B2oBXOGRfsf2kU7OFivny6ivdZOa4uCnfZQwAe06mVn6LUQnEsF0gi6YrgOM6Yj7eutF%2B8B%2FOsmNNgECU%2BPamDcPBDFYXGgYlKACnJXmvgFt; xman_us_f=x_locale=en_US&x_l=0&x_c_chg=0&x_as_i=%7B%22aeuCID%22%3A%2205dfaa54140e4cf085326af94b3e8872-1637645907156-01457-30NUWwU%22%2C%22af%22%3A%2234745%22%2C%22affiliateKey%22%3A%2230NUWwU%22%2C%22channel%22%3A%22AFFILIATE%22%2C%22cn%22%3A%2210008100042%22%2C%22cv%22%3A%221%22%2C%22isCookieCache%22%3A%22N%22%2C%22ms%22%3A%221%22%2C%22pid%22%3A%22945193473%22%2C%22tagtime%22%3A1637645907156%7D&acs_rt=557e56da2e85497fa4794b3e26d1808e; aeu_cid=05dfaa54140e4cf085326af94b3e8872-1637645907156-01457-30NUWwU; af_ss_a=1; af_ss_b=1; aep_usuc_f=site=glo&c_tp=USD&region=US&b_locale=en_US; traffic_se_co=%7B%7D; AKA_A2=A; _m_h5_tk=d8443ff08b62b4d41781b19988b59e8b_1637765961354; _m_h5_tk_enc=87243f40caf60f40ef62ccd850555583; xlly_s=1; _gid=GA1.2.2114043378.1637763803; _ga=GA1.1.550171611.1636859596; aep_history=keywords%5E%0Akeywords%09%0A%0Aproduct_selloffer%5E%0Aproduct_selloffer%094001309312006%0932859335286%091005003036026930%0910000251099979%091005003065070126%091005003574225553%091005002927225090%094000880206247; _ga_VED1YSGNC7=GS1.1.1637763803.27.1.1637765825.0; isg=BMvLGhItLgwbZXLWUzPVCZ4MWm-1YN_i0pmxJj3Ie4phXOu-xTJUMm-9MkSyzzfa; tfstk=cXqNB646cGIZdDmfyciV5xhA6iiOaYruDBkjSPl_QsH1VdPjasjXMvq3e2uWLI0G.; l=eBQlEaF4goQKGjbGBO5Bnurza77TzIRb4KFzaNbMiInca69fOFaxTOCdLBFp5dtjQtC3PetyzAmWidLHR3jR2xDDBjAHdZqn3xvO.; intl_common_forever=bRIvHbMd0cpwzqc8tfJ/4BdUGLj/gKxTnFaZAzuyTHXAr9tcUqxGGQ==; JSESSIONID=B1950BD62D6B145BD689E242A0D67868; RT="z=1&dm=aliexpress.com&si=bce3fd74-d45b-4b69-9861-0bbc877227fb&ss=kwdma25e&sl=4&tt=6uf&obo=3&rl=1&nu=bvu01ma5&cl=16fia&ld=1pq1g&r=hq4ssqnd&ul=1pq1h"'
    cookie = SimpleCookie()
    cookie.load(cookie_string)
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    return cookies


def remove_tag(description):
    if description:
        description = description.strip()
        description = description.replace("\t", "")
        description = description.replace("\n", "")
        description = description.replace("*", "")
        description = description.replace("[xlmodel]-[photo]-[0000]", "")
        description = description.replace("modname=ckeditor", "")
        description = description.encode('ascii', 'ignore')
        description = description.decode()
        return description


def current_price(response):
    price = response.xpath(
        '//div[@class="product-price-current"]/span[@class="product-price-value"]/text()').get()
    return remove_tag(price.replace('US $', ''))


user_agent_list = [
    # Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.30',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
    # Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0'
]


def image_html(image_list, title):
    img_template = """<div class=self-adaption style='margin-bottom:10px;'>
    <img style='max-width: 1000px;' title='{}' src='{}' />
    </div>"""
    final_img_list = []
    for img in image_list:
        final_imag = img.replace(
            '//', 'https://') if img.startswith('//') else img
        # image = img_template.format(title, remove_tag(final_imag))
        final_img_list.append(img_template.format(title, final_imag))
    return final_img_list


def spect_table(specs_dic):
    table = '<TABLE class=ke-zeroborder border=0 cellSpacing=0 cellPadding=0 width="100%">'
    table_end = '</table>'
    tbody = "<tbody>"
    tbody_end = "</tbody>"
    tr = ""
    for k, v in specs_dic.items():
        tr += f"<tr><td width=131 >{k}</td><td width=365>{v}</td></td></tr>"
    return f'{table}{tbody}{tr}{tbody_end}{table_end}'


def RemoveBannedWords(word):
    pattern = re.compile(r"\d+\s*?[x*]\s+?", re.I)
    return pattern.sub("", word)


def pack_inc(specs_dic):
    ul = '<ul>'
    ul_end = '</ul>'

    li = ""
    for k in specs_dic:
        k = RemoveBannedWords(k)
        li += f"<li>{k}</li>"
    return f'{ul}{li}{ul_end}'


def sku_color_size_list(sku_props):
    sku_size_list = []
    sku_color_list = []
    if sku_props is None:
        return sku_color_list, sku_size_list
    for value in sku_props:
        property_name = value.get('skuPropertyName')
        property_values = value.get('skuPropertyValues')
        if 'Color' in property_name:
            sku_color_list.extend(
                [x.get('propertyValueName') for x in property_values])

        if 'Size' in property_name:
            sku_size_list.extend([x.get('propertyValueName')
                                  for x in property_values])
    return sku_color_list, sku_size_list


def check_model(dict):
    model_name = dict.get('Model Name', None)
    model_number = dict.get('Model Number', None)
    if model_number:
        return model_number
    elif model_name:
        return model_name
    else:
        return ''


def cleaned_image_description(description_img):
    images = []
    for img in description_img:

        if img is not None:
            img = remove_tag(img)
            final_imag = re.sub(r'^//', 'https://', img)
            images.append(final_imag)
    return images


def key_exists(product, key1, key2):
    if key1 in product:
        return key1
    else:
        return key2


def tag_exist(product, key1, key2):
    k1 = product.css(key1).get()
    k2 = product.css(key2).get()
    return k1 if k1 else k2


def get_random_agent():
    return choice(user_agent_list)


def find_categories(breadcumb):
    cat_list = []
    for cat in breadcumb:
        id = int(cat.get('cateId'))
        if id > 0:
            cat_list.append(cat.get('name'))
    if len(cat_list) >= 3:
        category = cat_list[0]
        subcategory = cat_list[1]
        supercategory = cat_list[2]
    elif len(cat_list) == 2:
        category = cat_list[0]
        subcategory = cat_list[1]
        supercategory = None
    elif len(cat_list) == 1:
        category = cat_list[0]
        subcategory = None
        supercategory = None
    else:
        category = None
        subcategory = None
        supercategory = None
    return {'cat': category, 'sub': subcategory, 'sup': supercategory}


def json_output(data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
