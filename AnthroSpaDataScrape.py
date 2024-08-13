import pandas as pd
import requests
from bs4 import BeautifulSoup

def process_product(soup, product_url):
    product_name = None
    product_images = []
    product_description = None
    product_price = None
    product_availability = None

    # Getting the product name
    name_tags = soup.find_all("div", class_='tfRE5M')
    for tag in name_tags:
        title_tag = tag.find("h1", class_='OXQzmM')
        if title_tag:
            product_name = title_tag.get_text(strip=True)
            break

    # Getting the images of the product
    image_tags = soup.find_all("div", attrs={'data-index': True})
    for div_tag in image_tags:
        img_tag = div_tag.find("img")
        if img_tag and 'src' in img_tag.attrs:
            img_src = img_tag['src']
            if not img_src.startswith('data:image'):
                product_images.append(img_src)

    # Getting the product description
    description_tags = soup.find_all("div", class_='vaI0UH')
    for tag in description_tags:
        title_tag = tag.find("pre", class_='skK8UF')
        if title_tag:
            product_description = title_tag.get_text(strip=True)
            break

    # Getting the price of the product
    price_tags = soup.find_all("div", class_='Vn31tB')
    for tag in price_tags:
        price_span = tag.find("span", attrs={"data-hook": "formatted-primary-price"})
        if price_span:
            product_price = price_span.get_text(strip=True)
            break

    # Getting the availability of the product
    availability_tags = soup.find_all("div", class_='OHgko7 QfrfFD cell')
    for tag in availability_tags:
        button_tag = tag.find("button")
        if button_tag:
            if button_tag.get("aria-disabled") == 'false':
                product_availability = "In Stock"
            elif button_tag.get("aria-disabled") == 'true':
                product_availability = "Out of Stock"
            break

    return {
        "Name": product_name,
        "URL": product_url,
        "Images": product_images,
        "Description": product_description,
        "Price": product_price,
        "Availability": product_availability
    }

df = pd.read_csv("...AnthroSpaURL.csv", header=0) #enter csv file with all of the URLs

reviewDf = pd.DataFrame(columns=["Name", "URL", "Images", "Description", "Price", "Availability"])

processed_data = []

for index, row in df.iterrows():
    product_url = row['URL']  # Using 'URL' column directly

    print("Product URL:", product_url)  # Debug print to check Product URL

    try:
        response = requests.get(product_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            processed_product = process_product(soup, product_url)
            if processed_product:
                processed_data.append(processed_product)  # Append processed product to the list
        else:
            print("Failed to fetch product page. Status code:", response.status_code)
    except Exception as e:
        print("An error occurred:", e)

reviewDf = pd.DataFrame(processed_data)  # Create DataFrame from the processed data
reviewDf.to_csv("AnthroSpaDataScrape.csv", index=False)