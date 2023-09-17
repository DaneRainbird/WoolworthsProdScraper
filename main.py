'''
main.py
Author: Dane Rainbird (hello@danerainbird.me)
Last Edited: 2023-09-17

A script to get all the products from the Woolworths website and save them to a JSON file.
Running this script behind a VPN or proxy is recommended, as Woolworths will often start blocking requests if you make too many.

This script will create two files:
    - categories.json: A JSON file containing the categories and their URLs
    - products.json: A JSON file containing the products and their information
'''

import requests, json, os, time, random

BASE_URL = "https://www.woolworths.com.au"
CATEGORIES_INFO = "https://www.woolworths.com.au/apis/ui/PiesCategoriesWithSpecials/"
CATEGORIES_URL_BASE = "https://www.woolworths.com.au/apis/ui/browse/category"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
    'Host': 'www.woolworths.com.au',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

# Get a list of the categories from the API
print("Getting categories info...")
response = requests.get(CATEGORIES_INFO, headers=HEADERS)
if response.status_code == 200:
    data = response.json()
else:
    print("Error with loading CATEGORIES_INFO: " + str(response.status_code))
    exit()

# Get the relevant info (URL + name) for each category
categoryParams = {}
for category in data['Categories']:
    if category['NodeId'] == 'specialsgroup':
        continue

    categoryFriendlyName = category['UrlFriendlyName']
    categoryNodeId = category['NodeId']
    name = category['Description']
    location = "/shop/browse/" + category['UrlFriendlyName']

    categoryParam = {
        "categoryId": categoryNodeId,
        "formatObject": "{'name': '" + name + "'}", # The Woolworths API requires a formatObject parameter, but it seems to only need the name
        "url": location
    }

    categoryParams[categoryFriendlyName] = categoryParam

print("Categories info loaded.")

# Save categories to a file
if not os.path.exists('categories.json'):
    with open('categories.json', 'w', encoding='utf-8') as categoryFile:
        json.dump(categoryParams, categoryFile)

products = []

# Get products from the API for each category
for category in list(categoryParams.keys()):

    # Skip the front-of-store category as this is dependent on the store location
    if category == 'front-of-store':
        continue

    # Wait a random amount of time between 1 and 5 seconds to try and avoid getting blocked
    timeToWait = 1 + (5 - 1) * random.random()
    print("Waiting " + str(timeToWait) + " seconds...")
    time.sleep(timeToWait)

    response = requests.get(CATEGORIES_URL_BASE, params=categoryParams[category], headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
    else:
        print("Error with loading products in category " + category + ": " + str(response.status_code))
        exit()

    print("Now getting products for category: " + category)
    for product in data['Bundles']:
        # Get the specific product data
        specificProductData = product['Products'][0]
        productData = {
            "name": specificProductData['Name'],
            "urlFriendlyName": specificProductData['UrlFriendlyName'],
            "stockCode": specificProductData['Stockcode'],
            "price": specificProductData['Price'],
            "unit": specificProductData['Unit'],
            "IsOnSpecial": specificProductData['IsOnSpecial'],
            "InstoreIsOnSpecial": specificProductData['InstoreIsOnSpecial'],
            "url": BASE_URL + '/shop/productdetails/' + str(specificProductData['Stockcode']) + '/' + specificProductData['UrlFriendlyName'],
            "imageUrl": specificProductData['LargeImageFile'],
            "category": category
        }

        products.append(productData)

    # Save products to a file
    with open('products.json', 'a', encoding='utf-8') as productFile:
        json.dump(products, productFile)
        productFile.write("\n")
            
    print("Products for category " + category + " loaded.")