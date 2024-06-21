import requests
import re
import csv
import datetime
import os
import time
import sys
import json
from requests_html import HTMLSession

data_json = sys.argv[1]
data = json.loads(data_json)

headers = {
    "Cookie": data
}

completed_file = os.path.expanduser("~/Desktop/completed_urls.txt")
csv_filename = os.path.expanduser("~/Desktop/product_data.csv")

# Read completed URLs from file
if os.path.exists(completed_file):
    with open(completed_file, 'r', encoding='utf-8') as f:
        completed_urls = set(line.strip() for line in f)
else:
    completed_urls = set()

def save_completed_url(url):
    with open(completed_file, 'a', encoding='utf-8') as f:
        f.write(url + '\n')

def get_data(endpoint):
    return requests.get(endpoint, headers=headers, timeout=3000).text

def get_html(endpoint):
    session = HTMLSession()
    response = session.get(endpoint, headers=headers, timeout=3000)
    return response.html

def get_data_by_xpath(response, xpath):
    return response.xpath(xpath)

def extract_product_data(html):
    items = html.find('.SizeSwatch__Item')
    product_data = []
    for item in items:
        sku = item.find('input', first=True).attrs.get('data-sku')
        value = item.attrs.get('data-value')
        quantity = item.find('label', first=True).attrs.get('data-quantity')
        product_data.append((sku, value, int(quantity)))
    return product_data

def get_image_links(response):
    image_links = []
    img_tags = response.find('.Product__Slideshow img')
    for img in img_tags:
        if 'data-original-src' in img.attrs:
            img_url = img.attrs['data-original-src']
        elif 'src' in img.attrs:
            img_url = img.attrs['src']
        if img_url.startswith('//'):
            img_url = 'https:' + img_url
        image_links.append(img_url)
    return ",".join(image_links)


def retry_request(endpoint, headers, retries=5, delay=5):
    for attempt in range(retries):
        try:
            session = HTMLSession()
            response = session.get(endpoint, headers=headers, timeout=3000)
            return response.html
        except ConnectionResetError as e:
            print(f"Connection reset error: {str(e)}. Retrying ({attempt + 1}/{retries})...")
            time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}. Retrying ({attempt + 1}/{retries})...")
            time.sleep(delay)
    raise Exception(f"Failed to get response from {endpoint} after {retries} retries")


def convert_dict2str(dict):
    items = [value for value in dict.values()]
    data_str = "\n".join(items)
    return data_str

def find_by_pattern(data_str, pattern):
    match = re.search(pattern, data_str)
    if match:
        return match.group(1)
    else:
        return None

def get_tabs_info(response):
    tabs_info = {}
    tabs = response.find('.tab')
    for tab in tabs:
        label_element = tab.find('.tab-label', first=True)
        content_element = tab.find('.tab-content', first=True)
        if label_element and content_element:
            label = label_element.text.strip()
            content = content_element.text.strip()
            tabs_info[label] = content
    return tabs_info

def get_prices(response):
    def clean_price(price):
        return price.replace("€", "").replace(".", "").replace("- ", "").strip()

    try:
        discount_pr = get_data_by_xpath(response, "/html/body/div[8]/main/div[1]/section/div[1]/div[2]/div/div/div[1]/div[1]/div[4]/div[1]/div/span[2]")[0].text
    except IndexError:
        discount_pr = None

    if discount_pr and "%" in discount_pr:
        Retail_Price = get_data_by_xpath(response, "/html/body/div[8]/main/div[1]/section/div[1]/div[2]/div/div/div[1]/div[1]/div[4]/div[1]/div/span[1]")[0].text
        Discount = get_data_by_xpath(response, "/html/body/div[8]/main/div[1]/section/div[1]/div[2]/div/div/div[1]/div[1]/div[4]/div[1]/div/span[2]")[0].text
    else:
        Retail_Price = get_data_by_xpath(response, "/html/body/div[8]/main/div[1]/section/div[1]/div[2]/div/div/div[1]/div[1]/div[4]/div[1]/div/span")[0].text
        Discount = ""

    Retail_Price = clean_price(Retail_Price)
    if Discount:
        Discount = clean_price(Discount)

    return Retail_Price, Discount

pages_pattern = "https:\/\/stores\.antonioli\.eu\/sitemap_products_[^<\s]+"
product_pattern = "https:\/\/stores\.antonioli\.eu\/products\/[^<\s]+"

pages_link = re.findall(pages_pattern, get_data("https://stores.antonioli.eu/sitemap.xml"))
product_links = []
for page in pages_link:
    product_links.extend((re.findall(product_pattern, get_data(page))))

csv_headers = ["ProductUrl", "Brand", "Name", "Categories", "Retail_Price", "Discount", "SKU", "Size", "InStock", "Image_Links", "color", "Madein", "Composition", "ModelCode", "ItemID", "Height", "Width", "Depth", "Description", "Details"]

with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    
    # Write headers only if file is empty
    if os.stat(csv_filename).st_size == 0:
        writer.writerow(csv_headers)

    for product in product_links:
        if product in completed_urls:
            continue

        try:
            response = retry_request(product, headers)
            ProductUrl = product
            Brand = get_data_by_xpath(response, "/html/body/div[8]/main/div[1]/section/div[1]/div[2]/div/div/div[1]/div[1]/div[2]/h2/a")[0].text
            Name = get_data_by_xpath(response, "/html/body/div[8]/main/div[1]/section/div[1]/div[2]/div/div/div[1]/div[1]/div[3]/h2")[0].text
            Categories = " > ".join([breadcrumb.text for breadcrumb in response.find('#uncomplicated-breadcrumbs a')])
            Retail_Price, Discount = get_prices(response)
            Product_Data = extract_product_data(response)
            Tab_Labels = get_tabs_info(response)
            converted2str = convert_dict2str(Tab_Labels)
            Image_Links = get_image_links(response)
            color = find_by_pattern(converted2str, "▪ (.+?)\n")
            Madein = find_by_pattern(converted2str, "Made in: (.+?)\n")
            Composition = find_by_pattern(converted2str, "Composition: (.+?)\n")
            ModelCode = find_by_pattern(converted2str, "Model Code: (.+?)\n")
            ItemID = find_by_pattern(converted2str, "Item ID: (.+?)\n")
            Height = find_by_pattern(converted2str, "Height (.+?)\n")
            Width = find_by_pattern(converted2str, "Width (.+?)\n")
            Depth = find_by_pattern(converted2str, "Depth (.+?)\n")
            Description = Tab_Labels.get("Descrizione")
            if Description:
                Description = Description.replace("\n", "")
            else:
                Description = ""

            Details = Tab_Labels.get("Details")
            if Details:
                Details = Details.replace("\n", "")
            else:
                Details = ""

            if len(Product_Data) > 0:
                for x in Product_Data:
                    row = [ProductUrl, Brand, Name, Categories, Retail_Price, Discount, x[0], x[1], x[2], Image_Links, color, Madein, Composition, ModelCode, ItemID, Height, Width, Depth, Description, Details]
                    writer.writerow(row)
            else:
                row = [ProductUrl, Brand, Name, Categories, Retail_Price, Discount, "UNI", "UNI", 0, Image_Links, color, Madein, Composition, ModelCode, ItemID, Height, Width, Depth, Description, Details]
                writer.writerow(row)

            # Save completed URL
            save_completed_url(product)
            completed_urls.add(product)

        except Exception as e:
            print(f"Error processing product {product}: {str(e)}")
            continue
