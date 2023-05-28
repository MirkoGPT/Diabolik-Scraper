# Diabolik Comics Scraper

This Python script scrapes data about Diabolik comics from [Diabolik's official website](https://www.diabolik.it/), and saves the scraped data into a CSV file. The script also downloads the cover images for each comic. You can use the CSV file and images with the database of your choice to create all necessary entries. 

## Features

- Scrapes the following data for each comic:
  - Title
  - Plot
  - Publication date
  - Issue number
  - Series
  - Publisher
- Downloads the cover image for each comic.
- Prompts the user to input the initial link to start scraping from, the series name, and the desired path to save the scraped data and images.

## Prerequisites

Before running this script, ensure you have the following Python packages installed:

- `beautifulsoup4`: Parses HTML and extracts data.
- `requests`: Sends HTTP requests to the website.
- `dateparser`: Parses dates and converts them into a standard format.
- `PIL` (Pillow): Opens and checks the size of images.
- `unidecode`: Removes accents from characters.

You can install these packages using pip:

```sh
pip install beautifulsoup4 requests dateparser pillow unidecode
```


## How to Use

1. Navigate to Diabolik's official website.
2. Select an option under the "Albi" menu. In some cases, you may also need to select the desired year. Copy the link.
3. Run the script in a Python environment where all the prerequisites are installed.
4. When prompted, input the initial link to start scraping from (the one you copied in step 2), the name of the series, and the desired path to save the scraped data and images. If you leave the path empty, the data and images will be saved in the current directory.
5. The script will start scraping the data and downloading the images. Upon completion, you can find the scraped data in a CSV file and the images in a 'Covers' subdirectory at the specified path.