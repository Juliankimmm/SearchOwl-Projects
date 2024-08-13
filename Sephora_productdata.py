import pandas as pd
import requests
from bs4 import BeautifulSoup

df = pd.read_csv("D:\\Windows D\\Downloads\\testSephora - Sheet1.csv")

# Create a list to store processed data
processed_data = []

def find_brand(product_url, soup):
    brand_tag = soup.find('a', {'data-at': 'brand_name'})
    if brand_tag:
        brand_name = brand_tag.text.strip()
        print(f"Found brand: {brand_name} for URL: {product_url}")
        return brand_name
    else:
        print(f"No brand found for URL: {product_url}")
        return None

def check_no_sku(soup):
    """
    Checks if the page contains the "No Available SKU" message.
    Returns True if the message is found, otherwise False.
    """
    try:
        print("Checking for 'No Available SKU'...")
        
        # Find the div with data-comp="ProductPage"
        no_sku_tag = soup.find('div', {'data-comp': 'ProductPage'})
        
        if no_sku_tag:
            print("Div with data-comp='ProductPage' found.")
            print("HTML of the div:")
            print(no_sku_tag.prettify())  # Pretty print the HTML of the found div
            print(f"Text in div: '{no_sku_tag.text.strip()}'")
            if "No Available sku" in no_sku_tag.text:
                print("No Available SKU detected.")
                return True
            else:
                print("No Available SKU not found in the div.")
        else:
            print("Div with data-comp='ProductPage' not found.")
        
        return False
    except Exception as e:
        print(f"An error occurred while checking for 'No Available SKU': {e}")
        return False

# Iterate through products
for index, row in df.iterrows():
    print(f"Processing product at index {index}...")
    product_url = row['URL']
    product_name = row['Name']
    product_images = row['images']
    product_description = row['Description']
    product_sales = row['Sale Price']
    product_price = row['Original Price']
    product_ingredients = row['List of ingredients']
    product_rating = row['Rating']
    product_reviews = row['Number of reviews']
    product_sizes = row['Sizes']

    try:
        print(f"Fetching product page: {product_url}")
        response = requests.get(product_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code == 200:
            print(f"Successfully fetched product page: {product_url}")
            soup = BeautifulSoup(response.content, 'html.parser')

            # Check for 'No Available SKU'
            if check_no_sku(soup):
                print(f"Skipping URL due to 'No Available SKU': {product_url}")
                continue  # Skip to the next product

            # Extract brand information
            product_brand = find_brand(product_url, soup)
        else:
            print(f"Failed to fetch product page. Status code: {response.status_code}")
            product_brand = None
    except Exception as e:
        print(f"An error occurred while fetching product page: {e}")
        product_brand = None

    # Store the product data in a dictionary
    product_data = {
        "URL": product_url,
        "Name": product_name,
        "Images": product_images,
        "Description": product_description,
        "Sale Price": product_sales,
        "Original Price": product_price,
        "Ingredients": product_ingredients,
        "Rating": product_rating,
        "Number of reviews": product_reviews,
        "Sizes": product_sizes,
        "Brand": product_brand
    }

    # Append the dictionary to the processed_data list
    processed_data.append(product_data)
    print(f"Data for URL {product_url} appended to processed_data.")

# Create a DataFrame from the processed_data list
reviewDf = pd.DataFrame(processed_data)

# Save the DataFrame to a CSV file
output_file = "sephora_datascrape.csv"
reviewDf.to_csv(output_file, index=False)
print(f"Data successfully saved to {output_file}")