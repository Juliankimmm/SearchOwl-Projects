import pandas as pd
import requests
from bs4 import BeautifulSoup
import html
import re

def clean_fragrance_text(fragrance_text):
    # Remove unwanted words and characters
    clean_text = re.sub(r'\b(and|Choose from|-)\b', '', fragrance_text)
    # Replace spaces with commas
    clean_text = re.sub(r'\s+', ',', clean_text)
    # Remove leading commas
    clean_text = clean_text.lstrip(',')
    return clean_text

def remove_duplicate_commas(clean_text):
    # Remove duplicate commas
    cleaned_text = re.sub(r',+', ',', clean_text)
    return cleaned_text

df = pd.read_csv("file.csv", header=0) #the csv file with all of the links (I have shared in email)

reviewDf = pd.DataFrame(columns=["Name", "URL", "Images", "Description", "Fragrance", "Ingredients", "Price", "Size", "Availability"])

def process_product(product_data, product_url):
    product_name = product_data.get('data', {}).get('name', "")
    print('Product name:', product_name)  # Debug print to check product name

    if not product_name:
        print("Product name is missing. Skipping this product.")
        return

    # Extracting images
    images_data = product_data.get('data', {}).get('images', {}).get('data', [])
    images = [image.get('absolute_url', '') for image in images_data]

    # Extracting fragrance from short description
    short_description = product_data.get('data', {}).get('short_description', "")
    fragrance = None
    if "Fragrance:" in short_description:
        fragrance_text = short_description.split("Fragrance:")[1].split("</p>")[0].strip()
        fragrance_strip = clean_fragrance_text(fragrance_text)
        fragrance_strip = remove_duplicate_commas(fragrance_strip)  # Remove duplicate commas
        soup = BeautifulSoup(fragrance_strip, 'html.parser')
        fragrance = html.unescape(soup.get_text())

    # Extracting ingredients
    ingredients = None
    if "Ingredients:" in short_description:
        ingredients_text = short_description.split("Ingredients:")[1].split("</p>")[0].strip()
        soup = BeautifulSoup(ingredients_text, 'html.parser')
        ingredients = html.unescape(soup.get_text())

    # Extracting size from short description
    size = None
    if "Weight:" in short_description:
        size_text = short_description.split("Weight:")[1].split("</p>")[0].strip()
        soup = BeautifulSoup(size_text, 'html.parser')
        size = html.unescape(soup.get_text())
    elif "Size:" in short_description:
        size_text = short_description.split("Size:")[1].split("</p>")[0].strip()
        soup = BeautifulSoup(size_text, 'html.parser')
        size = html.unescape(soup.get_text())

    # Extracting description
    description = None
    description_text = short_description.split("Description:")[1].split("</p>")[0].strip()
    soup = BeautifulSoup(description_text, 'html.parser')
    description = html.unescape(description_text.encode('utf-8').decode('utf-8'))

    # Extracting other required information
    price = product_data.get('data', {}).get("price", {}).get("high_formatted", "")

    # Determine availability
    badges = product_data.get('data', {}).get("badges", {})
    inventory = product_data.get('data', {}).get("inventory", {})
    availability = 0 if badges.get("out_of_stock", False) else inventory.get("lowest", None)

    return {
        "Name": product_name,
        "URL": product_url,
        "Images": '\n'.join(images),  # Join images with newline characters
        "Description": description,
        "Fragrance": fragrance,
        "Ingredients": ingredients,
        "Price": price,
        "Size": size,
        "Availability": availability
    }

processed_data = []

for index, row in df.iterrows():
    product_url = row['URL ']  # Adjusted to use 'URL' column directly without additional processing
    product_id = product_url.split('/')[-1].split('?cp')[0]
    api_url = f"https://cdn5.editmysite.com/app/store/api/v28/editor/users/133093760/sites/169938646661493946/store-locations/11eaca2f0bf44717ba9d54ab3a322722/products/{product_id}?include=images,options,modifiers,category,media_files,fulfillment,discounts,subscriptions&cache-version=2023-11-13"

    print("API URL:", api_url)  # Debug print to check API URL

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            product_data = response.json()
            processed_product = process_product(product_data, product_url)
            if processed_product:
                processed_data.append(processed_product)  # Append processed product to the list
        else:
            print("Failed to fetch product data. Status code:", response.status_code)
    except Exception as e:
        print("An error occurred:", e)

reviewDf = pd.DataFrame(processed_data)  # Create DataFrame from the processed data
reviewDf.to_csv("ChronicallyCleantest.csv", index=False)