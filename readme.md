# Diabolik Comics Scraper

This Python script scrapes data about Diabolik comics from https://www.diabolik.it/ and saves the scraped data into a CSV file. The script also downloads the cover images for the comics.

## Features

- Scrapes the following data for each comic:
  - Title
  - Plot
  - Date
  - Issue number
  - Series
  - Publisher
- Downloads the cover image for each comic.
- Asks the user for the initial link to start scraping from, the series, and the desired path to save the scraped data and images.

## Prerequisites

Before running this script, you need to install the following Python packages:

- `beautifulsoup4`: For parsing HTML and extracting data.
- `requests`: For sending HTTP requests to the website.
- `dateparser`: For parsing dates and converting them into a standard format.
- `PIL`: For opening and checking the size of the images.
- `unidecode`: For removing accents from characters.

You can install these packages using pip:

```
pip install beautifulsoup4 requests dateparser pillow unidecode
```


## How to Use

1. Browse Diabolik's website.
2. Select an option under the menu "Albi". In some cases you may have to select also the desired year. Copy the link.
2. Run the script in a Python environment where all the prerequisites are installed.
3. When prompted, enter the initial link to start scraping from (the one you copied in step 2), the name of the series, and the desired path to save the scraped data and images. If you leave the path empty, the data and images will be saved in the current directory.
4. The script will then start scraping the data and downloading the images. Once it's done, you can find the scraped data in a CSV file and the images in a 'Covers' subdirectory at the specified path.
