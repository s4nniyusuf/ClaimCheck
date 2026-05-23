import time

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

HEADLESS = True

def set_up_browser(playwright):
    """Launch Chromium and return (browser, context, page)."""
    browser = playwright.chromium.launch(
        headless=HEADLESS,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-gpu"
        ]
        # Removed executable_path. Playwright finds chromium automatically
        # executable_path="/usr/bin/chromium"
        )
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    )
    page = context.new_page()
    return browser, context, page


def safe_get(parent, tag, class_name):
    """Return element text or None — never crashes on missing elements."""
    el = parent.find(tag, class_=class_name)
    return el.text.strip() if el else None


def structure_data(product_data: tuple):
    """ Structures the scraped data into a dictionary"""
    return {
        "product_name": product_data[0],
        "description": product_data[1],
        "rating": product_data[2],
        "reviews": product_data[3],
        "no_of_reviews": len(product_data[3])
    }


def parse_reviews(soup):
    """ Extract all reviews from the review soup. """
    review_container = soup.find("div", class_="cola -phxl -df -d-co")
    if not review_container:
        print("No reviews found. The page structure may have changed")
        return []
    
    reviews_data = []
    reviews = review_container.find_all("article", class_="-pvm -hr _bet")
    for review in reviews:
        # rating = safe_get(review, "div", "stars _m _al -mvs")
        review_title = safe_get(review, "h3", "-m -fs16 -pvm")
        review_text  = safe_get(review, "p", "-pvm")

        # concatenating review_title and review_text
        review = review_title + ". " + review_text

        reviews_data.append(review)

    time.sleep(2)
    return reviews_data


def scrape_data(page, soup):
    """ Scrapes product name, image url, product description, product rating and product reviews """
    product_name = soup.find("h1", class_="-fs20 -ptm -pbxs").text.strip()

    # img_el = soup.find("img", class_="-fw -fh")
    # image_url = img_el.get("src") or img_el.get("data-src") if img_el else None

    desc_el = soup.find("div", class_="markup -mhxl -pvxxl -oxa -sc")
    rating_el = soup.find("div", class_="-fs29 -yl5 -pvxs")

    if desc_el:
        description = desc_el.text.strip() 
    else:
        print("Could not extract description. The page structure may have changed")
        description = "N/A"
    
    if rating_el:
        rating = rating_el.text.strip() 
    else:
        print("Could not extract rating. The page structure may have changed")
        rating = "N/A"

    # see all link to all reviews
    see_all = soup.find("a", class_="btn _def _ti -mhm -fsh0")
    if see_all and see_all.text.strip().startswith("See All"):
        reviews_url = f"https://www.jumia.com.ng{see_all['href']}"
        print(f"Navigating to all reviews: {reviews_url}")

        try:
            page.goto(reviews_url, wait_until="domcontentloaded", timeout=15000)
            page.screenshot(path="/tmp/debug.png")
            page.wait_for_selector("div.cola", timeout=15000)
        except Exception as e:
            print("ERROR:", e)
            page.screenshot(path="/tmp/fail.png")
            raise

        reviews_soup = BeautifulSoup(page.content(), "lxml")
        reviews = parse_reviews(soup=reviews_soup)
        
    else:
        # Fall back to reviews already on the product page
        reviews = parse_reviews(soup=soup)

    # return product_name, image_url, description, rating, reviews
    return product_name, description, rating, reviews


def go_to_product_page(page, product_url: str):
    """ Access the product page and returns page soup object """
    try:
        page.goto(product_url, timeout=15000, wait_until="domcontentloaded")
        time.sleep(2)  # Wait to simulate human behaviour
        print("Page loaded successfully. ")
        # page.get_by_role("button", name="Accept All Cookies").click()
        # print("Cookies accepted")
        time.sleep(2)
        page.wait_for_selector("div.row ", timeout=15000)
        print("Page loaded successfully. Starting scrape")

        html = page.content()
        soup = BeautifulSoup(html, "lxml")
    except PlaywrightTimeoutError:
        print("Error: Page load timed out.")
        soup = None
    except Exception as e:
        print(f"An error occurred: {e}")
        soup = None
    finally:
        return page, soup


def scrape_jumia_product(product_url: str):
    with sync_playwright() as playwright:
        browser, context, page = set_up_browser(playwright=playwright)
        
        try:
            page, soup = go_to_product_page(page=page, product_url=product_url)
            if soup:
                product_data = scrape_data(page=page, soup=soup)
                product_info = structure_data(product_data=product_data)
                # print(f"Product Name: {product_info["product_name"]}")
                # print(f"Product Description: {product_info["description"]}")
                # print(f"Rating: {product_info["rating"]}")
                # print("Reviews")
                # print(f"------- {product_info["reviews"]}")
                return product_info
            else:
                print("Soup is None")
                return None
        finally:
            browser.close()
