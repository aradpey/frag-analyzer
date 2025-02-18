import requests
from urllib.parse import urlparse
import sys
import time
from bs4 import BeautifulSoup


def validate_fragrantica_url(url):
    """Validate if the given URL is a Fragrantica URL."""
    parsed_url = urlparse(url)
    return "fragrantica.com" in parsed_url.netloc


def download_and_parse_reviews(url):
    """Download HTML content and extract reviews and perfume image."""
    start_time = time.time()
    try:
        # Add headers to mimic a browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        elapsed_time = time.time() - start_time
        print(f"Download completed in {elapsed_time:.2f} seconds")

        # Parse the HTML content
        parse_start_time = time.time()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract perfume image URL
        image_element = soup.find("img", attrs={"itemprop": "image"})
        image_url = image_element["src"] if image_element else None

        # Extract reviews
        reviews = soup.find_all("div", attrs={"itemprop": "reviewBody"})

        # Extract and clean review texts
        review_texts = []
        for i, review in enumerate(reviews, 1):
            text = review.get_text(strip=True)
            if text:  # Only add non-empty reviews
                review_texts.append({"number": i, "text": text})

        parse_time = time.time() - parse_start_time
        print(f"Parsing completed in {parse_time:.2f} seconds")

        return {"reviews": review_texts, "image_url": image_url}

    except requests.RequestException as e:
        elapsed_time = time.time() - start_time
        print(f"Error downloading the page after {elapsed_time:.2f} seconds: {e}")
        return None


def main():
    total_start_time = time.time()
    if len(sys.argv) != 2:
        print("Usage: python fragrantica_scraper.py <fragrantica_url>")
        sys.exit(1)

    url = sys.argv[1]

    if not validate_fragrantica_url(url):
        print("Error: Please provide a valid Fragrantica URL")
        sys.exit(1)

    reviews = download_and_parse_reviews(url)
    if reviews:
        if len(reviews["reviews"]) > 0:
            print(f"\nFound {len(reviews['reviews'])} reviews:\n")
            print("-" * 50)
            for review in reviews["reviews"]:
                print(f"Review #{review['number']}:\n{review['text']}\n")
            print("-" * 50)
        else:
            print("No reviews found on this page.")

        if reviews["image_url"]:
            print(f"\nPerfume Image URL: {reviews['image_url']}")

        total_time = time.time() - total_start_time
        print(f"\nTotal operation completed in {total_time:.2f} seconds")


if __name__ == "__main__":
    main()
