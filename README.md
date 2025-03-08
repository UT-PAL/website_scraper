Website Scraper
A simple web scraper that crawls through websites recursively and extracts data such as titles, links, images, paragraphs, headings, and div content. It supports both static and dynamic pages, using BeautifulSoup for static pages and Playwright for JavaScript-heavy pages.

Features
Scrapes static web pages using BeautifulSoup for faster data extraction.
Scrapes dynamic, JavaScript-heavy pages using Playwright.
Recursively crawls pages up to a user-defined depth.
Supports extracting useful content like:
Titles
Links
Images
Paragraphs
Headings (h1, h2, h3, etc.)
Div content
Results are saved in a JSON format, with a unique timestamp for each crawl.
Installation
Requirements
Python 3.7 or higher

Dependencies:
requests – To make HTTP requests to fetch web pages.
beautifulsoup4 – To parse and extract data from static HTML pages.
playwright – To scrape dynamic pages that require JavaScript rendering.
gradio – For creating the user interface for the scraper.
Note: If you are running Playwright for the first time, you may need to install additional dependencies. You can do this by running:
python -m playwright install



Code Overview
Functions:
scrape_static_page(url):

Scrapes static pages (HTML without JavaScript) using BeautifulSoup.
Extracts titles, links, images, paragraphs, headings, and div content.
scrape_dynamic_page(url):

Scrapes dynamic pages (JavaScript-heavy) using Playwright.
Waits for page content to load before extracting data.
scrape_website(url, max_depth=2, depth=0):

Recursively scrapes a website, following internal links and collecting data for each page.
Stops when the maximum depth is reached or the page has already been visited.
gradio_scraper(url, depth):

Integrates with the Gradio interface to start the scraping process.
Returns scraped data as a JSON object.

Create a requirements.txt file
You can create a requirements.txt file for your environment to list all the dependencies:

requests
beautifulsoup4
playwright
gradio
