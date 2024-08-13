import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import re

# Load DataFrame from CSV
df = pd.read_csv("D:/Windows D/Downloads/Feloh URL.csv")

# Create DataFrame to store reviews
reviewDf = pd.DataFrame(columns=["name", "URL", "description", "ingredients", "directions", "details", "images", "availability"])

def clean_json_string(json_string):
    """Clean and preprocess the JSON string to handle common issues."""
    # Replace HTML entities and invalid characters
    json_string = json_string.replace('&#39;', "'").replace('&amp;amp;', '&')
    # Remove any invalid control characters
    json_string = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', json_string)
    return json_string

def clean_text(text):
    """Clean unwanted characters from text."""
    if text:
        text = text.replace('Â', '').replace('&quot;', '"').replace(',Â', ',').replace('-Â', '-').replace('â€¦', '...').replace('â€™', "'")
    return text

def extract_field(description, start_marker, end_marker=None):
    """Extract field content from the description based on start and optional end markers."""
    start_index = description.find(start_marker)
    if start_index == -1:
        return None
    start_index += len(start_marker)
    if end_marker:
        end_index = description.find(end_marker, start_index)
        if end_index == -1:
            return description[start_index:].strip()
        return description[start_index:end_index].strip()
    return description[start_index:].strip()

def process_product(soup, product_url):
    # Initialize variables
    product_name = None
    product_images = []
    product_description = None
    product_price = None
    product_ingredients = None
    product_directions = None 
    product_details = None 
    product_availability = None

    # Print the raw HTML for debugging
    try:
        raw_html = soup.prettify()
        print("Raw HTML:")
        print(raw_html)
    except Exception as e:
        print(f"An error occurred while printing raw HTML: {e}")

    # Get the availability
    add_to_cart = soup.find('input', {'id': 'addToCart'})
    if add_to_cart:
        availability_value = add_to_cart.get('value')
        if availability_value:
            product_availability = availability_value.strip()
            print(f"Product Availability: {product_availability}")

    # Extract JSON data
    script_tag = soup.find('script', type='application/ld+json')
    if script_tag:
        try:
            json_data = script_tag.string
            print("Raw JSON Text:")
            print(json_data)  # Print the raw JSON text
            
            # Clean the JSON data
            json_data = clean_json_string(json_data)
            
            # Parse JSON data
            try:
                data = json.loads(json_data)
            except json.JSONDecodeError as e:
                print(f"JSON decode error for URL {product_url}: {e}")
                return None  # Skip this product
            
            # Extract and print data
            product_name = data.get('name')
            raw_description = data.get('description', '')

            # Extract specific fields from the description
            product_description = extract_field(raw_description, 'Description', 'Ingredients')
            product_ingredients = extract_field(raw_description, 'Ingredients', 'Directions')
            product_directions = extract_field(raw_description, 'Directions', 'Details')
            product_details = extract_field(raw_description, 'Details')

            # Print extracted raw values
            print(f"Raw Description: {product_description}")
            print(f"Raw Ingredients: {product_ingredients}")
            print(f"Raw Directions: {product_directions}")
            print(f"Raw Details: {product_details}")

            # Clean the extracted text
            product_description = clean_text(product_description)
            product_ingredients = clean_text(product_ingredients)
            product_directions = clean_text(product_directions)
            product_details = clean_text(product_details)

            # Print cleaned values
            print(f"Cleaned Description: {product_description}")
            print(f"Cleaned Ingredients: {product_ingredients}")
            print(f"Cleaned Directions: {product_directions}")
            print(f"Cleaned Details: {product_details}")

            product_price = data.get('offers', {}).get('price', '')
            product_images = data.get('image', [])
            
            # Handling multiple images
            if isinstance(product_images, str):
                product_images = [product_images]
            else:
                product_images = [img for img in product_images if img]

            # Print values found
            print(f"Product Name: {product_name}")
            print(f"Product Price: {product_price}")
            print(f"Product Images: {product_images}")

        except Exception as e:
            print(f"An error occurred while processing product: {e}")

    return {
        "name": product_name,
        "URL": product_url,
        "images": product_images,
        "description": product_description,
        "price": product_price,
        "ingredients": product_ingredients,
        "directions": product_directions,
        "details": product_details,
        "availability": product_availability
    }

processed_data = []

for index, row in df.iterrows():
    product_url = row['URL']  # Using 'URL' column directly

    print("Product URL:", product_url)  # Debug print to check Product URL

    try:
        response = requests.get(product_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content.decode('utf-8', errors='ignore'), "html.parser")
            processed_product = process_product(soup, product_url)
            if processed_product:
                processed_data.append(processed_product)  # Append processed product to the list
        else:
            print("Failed to fetch product page. Status code:", response.status_code)
    except Exception as e:
        print("An error occurred:", e)

# Create DataFrame from the processed data
reviewDf = pd.DataFrame(processed_data)
reviewDf.to_csv("FelohScrape.csv", index=False)