# Working in Progress
# Scrapping price from amazon website using ASIN
# Usage: python amazon_product.py for reading the predefined ASINs
#        python amazon_product.py {ASIN} for reading price history of
#        particular ASIN
# 20180406

from lxml import html
import sys
import csv
import os
import requests
from exceptions import ValueError
from time import sleep
from random import randint
import datetime

def parse(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
    }
    
    try:
        # Retrying for failed requests
        for i in range(20):
            # Generating random delays
            sleep(randint(1,3))
            # Adding verify=False to avold ssl related issues
            response = requests.get(url, headers=headers, verify=False)

            if response.status_code == 200: 
                doc = html.fromstring(response.content)
                XPATH_NAME = '//h1[@id="title"]//text()'
                #XPATH_SALE_PRICE = '//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()'
                XPATH_SALE_PRICE = \
                '//td[@class="comparison_baseitem_column"]//span[@class="a-offscreen"]/text()'
                XPATH_ORIGINAL_PRICE = '//td[contains(text(),"List Price") or contains(text(),"M.R.P") or contains(text(),"Price")]/following-sibling::td/text()'
                XPATH_CATEGORY = '//a[@class="a-link-normal a-color-tertiary"]//text()'
                XPATH_AVAILABILITY = '//div[@id="availability"]//text()'

                RAW_NAME = doc.xpath(XPATH_NAME)
                RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
                RAW_CATEGORY = doc.xpath(XPATH_CATEGORY)
                RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)
                RAW_AVAILABILITY = doc.xpath(XPATH_AVAILABILITY)

                NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
                SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
                CATEGORY = ' > '.join([i.strip() for i in RAW_CATEGORY]) if RAW_CATEGORY else None
                ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else None
                AVAILABILITY = ''.join(RAW_AVAILABILITY).strip() if RAW_AVAILABILITY else None
                TIME = '{:%Y-%m-%d %H:%M}'.format(datetime.datetime.utcnow())

                if not ORIGINAL_PRICE:
                    ORIGINAL_PRICE = SALE_PRICE
                # retrying in case of captcha
                if not NAME:
                    raise ValueError('captcha')

                data = {
                    'NAME': NAME,
                    'SALE_PRICE': SALE_PRICE,
                    'CATEGORY': CATEGORY,
                    'ORIGINAL_PRICE': ORIGINAL_PRICE,
                    'AVAILABILITY': AVAILABILITY,
                    'URL': url,
                    'TIME': TIME
                }
                return data
            
            elif response.status_code==404:
                break

    except Exception as e:
        print e

def ReadAsin():
    # AsinList = csv.DictReader(open(os.path.join(os.path.dirname(__file__),"Asinfeed.csv")))
    AsinList = ['B075QLRSPK',
                'B0731KJVGG']

    extracted_data = []

    for i in AsinList:
        extracted_data = []
        url = "http://www.amazon.com/dp/" + i
        print "Processing: " + url
        # Calling the parser
        parsed_data = parse(url)
        if parsed_data:
            extracted_data.append(parsed_data)

        # Writing scraped data to csv filea

        # Initiate csv if not exist with header

        fieldnames = \
        ['NAME','SALE_PRICE','CATEGORY','ORIGINAL_PRICE','AVAILABILITY','URL','TIME']

        if not os.path.isfile('./' + i + '.csv'):
            with open(i+'.csv', 'a') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                writer.writeheader()
        
        # Writing data
        with open(i+'.csv', 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            for data in extracted_data:
                writer.writerow(data)

def ReadPricesAsin(asin):
    with open(asin+'.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row['SALE_PRICE'], row['TIME'])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        ReadAsin()
    else:
        print('reading price history of '+sys.argv[1])
        ReadPricesAsin(sys.argv[1])
