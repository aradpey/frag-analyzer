from flask import Flask, render_template, request, jsonify, Response
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import os
import logging
import json
import asyncio
from dotenv import load_dotenv
from fragrance_analyzer import FragranceAnalyzer
from time_analysis import TimeAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize the FragranceAnalyzer with the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
analyzer = FragranceAnalyzer(api_key=OPENAI_API_KEY)


def validate_fragrantica_url(url):
    """Validate if the given URL is a Fragrantica URL."""
    parsed_url = urlparse(url)
    return "fragrantica.com" in parsed_url.netloc


def extract_fragrance_name(soup):
    """Extract the fragrance name from the page."""
    try:
        # Try to find the main heading with the fragrance name
        heading = soup.find("h1", {"itemprop": "name"})
        if heading:
            return heading.text.strip()
        return "Unknown Fragrance"
    except:
        return "Unknown Fragrance"


async def analyze_reviews_async(reviews_text: str, fragrance_name: str):
    """Asynchronously analyze reviews and yield results as they become available."""
    try:
        analysis_result = await analyzer.analyze_reviews(reviews_text, fragrance_name)
        return analysis_result
    except Exception as e:
        logger.error(f"Error in analysis: {str(e)}")
        return {"error": str(e)}


def download_and_parse_reviews(url):
    """Download HTML content and extract reviews."""
    logger.info(f"Starting to process URL: {url}")
    timer = TimeAnalyzer().start()
    result = {
        "reviews": [],
        "stats": {},
        "error": None,
        "analysis": None,
        "image_url": None,
    }

    try:
        # Add headers to mimic a browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        logger.info("Downloading page content")
        with timer.measure_operation("download"):
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

        # Parse the HTML content
        logger.info("Parsing HTML content")
        with timer.measure_operation("parse"):
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract perfume image URL
            image_element = soup.find("img", attrs={"itemprop": "image"})
            if image_element and "src" in image_element.attrs:
                result["image_url"] = image_element["src"]
                logger.info(f"Found perfume image URL: {result['image_url']}")

            reviews = soup.find_all("div", attrs={"itemprop": "reviewBody"})
            logger.info(f"Found {len(reviews)} reviews")

            # Get fragrance name
            fragrance_name = extract_fragrance_name(soup)
            logger.info(f"Extracted fragrance name: {fragrance_name}")

            # Extract and clean review texts
            for i, review in enumerate(reviews, 1):
                text = review.get_text(strip=True)
                if text:  # Only add non-empty reviews
                    result["reviews"].append({"number": i, "text": text})

        # If we have reviews, analyze them
        if result["reviews"]:
            logger.info("Starting GPT analysis")
            with timer.measure_operation("analysis"):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                analysis = loop.run_until_complete(
                    analyze_reviews_async(
                        "\n".join(r["text"] for r in result["reviews"]), fragrance_name
                    )
                )
                loop.close()
                result["analysis"] = analysis
            logger.info("Completed GPT analysis")
            logger.info(f"Analysis result: {result['analysis']}")
            # Add fragrance name to the response
            result["fragrance_name"] = fragrance_name
        else:
            logger.warning("No reviews found to analyze")
            result["analysis"] = {"error": "No reviews found to analyze"}

        timer.set_review_count(len(result["reviews"]))
        result["stats"] = timer.finalize()
        logger.info(f"Final stats: {result['stats']}")

    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}", exc_info=True)
        result["error"] = f"Error downloading the page: {str(e)}"
    except Exception as e:
        logger.error(f"General error: {str(e)}", exc_info=True)
        result["error"] = f"An error occurred: {str(e)}"

    return result


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scrape", methods=["POST"])
def scrape():
    url = request.json.get("url", "")
    logger.info(f"Received scrape request for URL: {url}")

    if not url:
        logger.warning("No URL provided")
        return jsonify({"error": "Please provide a URL"})

    if not validate_fragrantica_url(url):
        logger.warning("Invalid Fragrantica URL")
        return jsonify({"error": "Please provide a valid Fragrantica URL"})

    result = download_and_parse_reviews(url)
    logger.info("Sending response back to client")
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
