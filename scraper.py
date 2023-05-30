"""
This script is used to scrape a website for comic book information. The user provides a starting URL for the scrape, 
the series name, and a directory to save the output. The script scrapes the website for relevant information, 
saves it in a CSV file, and downloads cover images.
"""

import csv
import os
import requests
import dateparser
import logging
import re
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from unidecode import unidecode

def get_user_input():
    start_url = input("Please enter the initial link where to start the scraping from: ")
    series = input("Please specify the series: ")
    path = input("Please specify the full path where you want to save the folder (Leave empty to save in the current directory): ")
    if not path:
        path = os.getcwd()
    return start_url, series, path

def setup_directories_and_logging(path, series):
    series_dir = os.path.join(path, series, 'Covers')
    os.makedirs(series_dir, exist_ok=True)
    logging.basicConfig(filename=os.path.join(path, series, 'error_log.txt'), level=logging.ERROR)
    return series_dir

def scrape_and_write_data(start_url, series, path, series_dir):
    error_list = []
    try:
        response = requests.get(start_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        item_elements = soup.find_all('div', class_='item-element')

        with open(os.path.join(path, series, 'output.csv'), 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(['Title', 'Plot', 'Date', 'Issue', 'Series', 'Publisher'])

            for item_element in item_elements:
                try:
                    process_item_element(item_element, writer, series, series_dir)
                except Exception as e:
                    log_and_append_error(error_list, f"Unexpected error occurred while processing item element: {e}")

    except requests.exceptions.RequestException as err:
        log_and_append_error(error_list, f"Error occurred: {err}")

    return error_list

def process_item_element(item_element, writer, series, series_dir):
    project_info = item_element.find('div', class_='project-info')
    if project_info:
        url = item_element.find('figure').find('a')['href']
        title = project_info.find('h2')
        if title:
            # Here we split the title_text string by the dash and strip leading and trailing whitespaces.
            # If there's no dash in the string, it will return the whole string.
            title_text = title.get_text().strip().split(' - ', 1)[-1]
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            write_data(soup, title_text, writer, series, series_dir)

def write_data(soup, title_text, writer, series, series_dir):
    plot_text, date_info, issue_info, title_text, price_text = extract_data(soup)
    writer.writerow([title_text, plot_text, date_info, issue_info, series, 'Astorina'])
    
    # Find the product-thumb-area div
    product_thumb_area = soup.find('div', class_='product-thumb-area')
    if product_thumb_area is not None:
        # Find all figure elements within this div
        image_elements = product_thumb_area.find_all('figure', class_='port-details-thumb-item')
    else:
        image_elements = []
    
    pattern = re.compile(r'https://www\.diabolik\.it/uploads/image_crop/.*\.jpg')
    unique_image_urls = list(set([img.find('img')['src'] for img in image_elements if img.find('img') and pattern.match(img.find('img')['src'])]))
    download_images(unique_image_urls, series_dir, issue_info)


def extract_data(soup):
    # Title
    title_section = soup.find("h1")
    title_text = title_section.get_text(strip=True) if title_section else "Title not available"

    # Price
    price_section = soup.find("span", class_="price")
    price_text = price_section.get_text(strip=True) if price_section else "Price not available"
    
    # Description/Plot
    desc_section = soup.find("div", class_="prod-details-info-content")
    plot_text = desc_section.p.get_text(strip=True).replace('"', '').replace("'", "") if desc_section and desc_section.p else "Plot information not available"

    # Issue Number
    issue_info = soup.find("div", class_="description-content")
    if issue_info:
        issue_text = issue_info.get_text(strip=True)
        issue_number = re.search(r'Inedito n.\s*(\d+)', issue_text)
        issue_text = issue_number.group(1) if issue_number else "Issue number not available"
    else:
        issue_text = "Issue number not available"
    
    # Release Date
    date_section = soup.find("div", class_="footer-item-right")
    if date_section:
        date_info = date_section.get_text(strip=True)
        formatted_date = dateparser.parse(date_info, languages=['it']).strftime('%b %Y') if date_info else "Date information not available"
    else:
        formatted_date = "Date information not available"

    return plot_text, formatted_date, issue_text, title_text, price_text

def download_images(unique_image_urls, series_dir, issue_info):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    for image_url in unique_image_urls:
        try:
            logging.info(f"Downloading image: {image_url}")
            response = requests.get(image_url, stream=True, headers=headers)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            if img.size == (603, 853):
                image_suffix = image_url.split('/')[-1]
                with open(os.path.join(series_dir, f'{issue_info}_{image_suffix}'), 'wb') as image_file:
                    for chunk in response.iter_content(chunk_size=128):
                        image_file.write(chunk)
            else:
                logging.error(f"Image size mismatch: {img.size} for URL: {image_url}")
        except requests.exceptions.RequestException as err:
            logging.error(f"Error occurred while downloading image: {err} URL: {image_url}")
        except Exception as e:
            logging.error(f"Unexpected error: {e} URL: {image_url}")

def log_and_append_error(error_list, error_message):
    logging.error(error_message)
    error_list.append(error_message)
    print(error_message)

def main():
    start_url, series, path = get_user_input()
    series_dir = setup_directories_and_logging(path, series)
    error_list = scrape_and_write_data(start_url, series, path, series_dir)
    if error_list:
        print("\nErrors occurred during the execution of the script:")
        for error in error_list:
            print(error)
    else:
        print("\nScript executed without errors.")

if __name__ == "__main__":
    main()
