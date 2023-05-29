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
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from unidecode import unidecode

# Ask the user for the initial link, the series and the desired path
start_url = input("Please enter the initial link where to start the scraping from: ")
series = input("Please specify the series: ")
path = input("Please specify the full path where you want to save the folder (Leave empty to save in the current directory): ")

# If path is empty, set it to the current directory
if not path:
    path = os.getcwd()

# Create directories for the series and covers if they don't exist
series_dir = os.path.join(path, series, 'Covers')
os.makedirs(series_dir, exist_ok=True)

# Setup logging
logging.basicConfig(filename=os.path.join(path, series, 'error_log.txt'), level=logging.ERROR)

# List to store errors to be displayed at the end of the execution
error_list = []

try:
    # Send a GET request to the main page
    response = requests.get(start_url)
    response.raise_for_status()

    # Parse the HTML content of the main page with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all div elements with the class 'item-element'
    item_elements = soup.find_all('div', class_='item-element')

    # Open a CSV file in write mode in the series directory
    with open(os.path.join(path, series, 'output.csv'), 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(['Title', 'Plot', 'Date', 'Issue', 'Series', 'Publisher'])

        for item_element in item_elements:
            project_info = item_element.find('div', class_='project-info')
            if project_info:
                title = project_info.find('h2')
                if title:
                    # Remove leading and trailing spaces from the title
                    title_text = title.get_text().strip()

                    # Replace spaces with hyphens, remove apostrophes, and remove accents from the title using unidecode
                    url_title = unidecode(title_text).replace(' ', '-').replace('\'', '')

                    # Construct the URL for the title's webpage
                    url = f"https://www.diabolik.it/commerce/prodotto/{url_title}"

                    # Send a GET request to the title's webpage
                    response = requests.get(url)

                    # Parse the HTML content of the title's webpage with BeautifulSoup
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Extract the plot, issue, and date from the webpage
                    plot_info = soup.find('div', class_='price-group').find_next_sibling('p')
                    date_info = soup.find('div', class_='footer-item-right').find('ul').find('li')
                    issue_info = soup.find('div', class_='description-content').find('p')

                    # Ensure that plot_info, date_info, and issue_info are not None before extracting their text
                    if plot_info and date_info and issue_info:
                        plot_text = plot_info.get_text().strip().replace('"', '')

                        # Extract issue number
                        issue_text = issue_info.find('b').next_sibling.strip()

                        # Convert the Italian month name to a month number
                        date = dateparser.parse(date_info.get_text(), languages=['it'])
                        formatted_date = date.strftime('%b %Y')

                        # Write the data to the CSV file
                        writer.writerow([title_text, plot_text, formatted_date, issue_text, series, 'Astorina'])

                        # Find the image URLs in the carousel
                        images = soup.select('.port-details-thumb-item img')

                        # Extract unique image URLs
                        unique_image_urls = list(set([img['src'] for img in images]))

                        # Download images
                        for image_url in unique_image_urls:
                            try:
                                # Construct image URL
                                response = requests.get(image_url, stream=True)
                                response.raise_for_status()

                                # The image URL was accessible, open it with PIL
                                img = Image.open(BytesIO(response.content))

                                # Only save the image if it's the correct size
                                if img.size == (603, 853):
                                    image_suffix = image_url.split('/')[-1]  # Extract the last part of the URL as the image suffix
                                    with open(os.path.join(series_dir, f'{issue_text}_{image_suffix}'), 'wb') as image_file:
                                        for chunk in response.iter_content(chunk_size=128):
                                            image_file.write(chunk)
                            except requests.exceptions.HTTPError as err:
                                error_message = f"HTTP Error occurred while downloading image: {err}"
                                logging.error(error_message)
                                error_list.append(error_message)
                                print(error_message)
                            except requests.exceptions.RequestException as err:
                                error_message = f"Error occurred while downloading image: {err}"
                                logging.error(error_message)
                                error_list.append(error_message)
                                print(error_message)

except requests.exceptions.HTTPError as err:
    error_message = f"HTTP Error occurred: {err}"
    logging.error(error_message)
    error_list.append(error_message)
    print(error_message)
except requests.exceptions.RequestException as err:
    error_message = f"Error occurred: {err}"
    logging.error(error_message)
    error_list.append(error_message)
    print(error_message)

if error_list:
    print("\nErrors occurred during the execution of the script:")
    for error in error_list:
        print(error)
else:
    print("\nScript executed without errors.")
