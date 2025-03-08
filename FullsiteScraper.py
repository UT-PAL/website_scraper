import json
#Fetches web pages
import requests
#Extracts data from HTML
from bs4 import BeautifulSoup
#ensure absolute url
from urllib.parse import urljoin, urlparse
#handles js-heavy pages
from playwright.sync_api import sync_playwright

import gradio as gr
import random
import time
from datetime import datetime
# Initialize global visited set. Prevents duplicate scraping
visited = set()

def scrape_static_page(url):
    """Scrapes a static page using BeautifulSoup (faster)."""
    try:
        headers = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"},
]

        response = requests.get(url, headers=random.choice(headers), timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "No Title"

        links = [urljoin(url, a["href"]) for a in soup.find_all("a", href=True)]
        images = [urljoin(url, img["src"]) for img in soup.find_all("img", src=True)]
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        headings = {f"h{i}":[h.get_text(strip=True) for h in soup.find_all(f"h{i}")] for i in range(1, 7)}
        div = [div.get_text(strip=True) for div in soup.find_all("div")]
        return {"url": url,
                 "title": title,
                   "links": list(set(links)),
                     "images": list(set(images)),
                     "paragraphs":str(paragraphs),
                     "headings":str(headings),
                     "div":str(div)
                     }
    
    except requests.RequestException as e:
        print(f"Failed to scrape {url}: {e}")
        return None

def scrape_dynamic_page(url):
    """Scrapes a JavaScript-heavy page using Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(url, timeout=10000)
            title = page.title()
            links = [urljoin(url, a.get_attribute("href")) for a in page.query_selector_all("a[href]")]
            images = [urljoin(url, img.get_attribute("src")) for img in page.query_selector_all("img[src]")]
            paragraphs = [p.inner_text for p in page.query_selector_all("p")]
            headings = {f"h{i}":[h.inner_text for h in page.query_selector_all(f"h{i}")] for i in range(1, 7)}
            div = [div.inner_text for div in page.query_selector_all("div")]
            data = {"url": url,
                     "title": title, 
                     "links": list(set(links)), 
                     "images": list(set(images)),
                     "paragraphs":str(paragraphs),
                     "headings":str(headings),
                     "div": str(div)
                     }
            browser.close()
            return data
        
        except Exception as e:
            print(f"Error loading {url}: {e}")
            browser.close()
            return None


#https://example.com (Depth 0)
#│
#├── https://example.com/page1 (Depth 1)
#│   ├── https://example.com/page2 (Depth 2)
#│   ├── https://example.com/blog (Depth 2)
#|       |----https://example.com/about (Depth 3)
#│   └── https://example.com/contact (Depth 2)



def scrape_website(url, max_depth=2, depth=0):
    """Recursively scrapes a full website."""
    if depth > max_depth or url in visited:
        return []
    
    visited.add(url)
    print(f"Scraping: {url} (Depth {depth})")
    
    parsed_url = urlparse(url)
#ParseResult(scheme='https', netloc='www.booking.com', path='/index.html', params='', query='aid=1535067&label=enxl-edge-ntp-topsites-curate-ana', fragment='')
    root_domain = parsed_url.netloc
    
    # Choose static or dynamic scraping
    if depth == 0:
        page_data = scrape_dynamic_page(url)  # Use Playwright for the first page
    else:
        page_data = scrape_static_page(url)  # Use BeautifulSoup for speed

    if not page_data:
        return []
    
    data = [page_data]

    # Recursively scrape internal links
    for link in page_data["links"]:
        if urlparse(link).netloc == root_domain:  # Only follow internal links
            data += scrape_website(link, max_depth, depth + 1)

    return data


def gradio_scraper(url,depth):
    visited.clear()
    result = scrape_website(url,max_depth=int(depth))
    # Generate a unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"result_{depth}.json"
    with open(filename, "w",encoding="utf-8") as f:
        json.dump(result, f,indent=4)

    return json.dumps(result, indent=4)

demo = gr.Interface(
    fn=gradio_scraper,
    inputs=[
        gr.Textbox(label="Enter root url to scrap",placeholder="https://example.com"),
        gr.Slider(minimum=1,maximum=5,step=1,label="Max Depth",value=1)
    ],
    outputs = gr.JSON(label="scraped data"),
    title="Website Scraper",
    description="Enter a website URL and select a crawl depth to scrape pages, links, texts and images.",
)
if __name__ == "__main__":
    demo.launch()