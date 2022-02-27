from setuptools import setup

setup(
    name='aliexpress-scraper',
    version='1.0',
    packages=['aliexpress', 'aliexpress.spiders'],
    url='https://www.fiverr.com/users/mazharali2021',
    license='',
    author='Mazhar Ali',
    author_email='mzr.ali@gmail.com',
    description='Aliexpress Data Scraping with google sheet support',
    install_requires=[
        'scrapy',
        'selenium',
        'webdriver-manager',
        'google-api-python-client',
        'google-auth-httplib2',
        'google-auth-oauthlib',
        'scrapy-selenium',
        'requests'


    ]

)
