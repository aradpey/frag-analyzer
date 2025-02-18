import openai
import json
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from analysis_modules import (
    analyze_seasonal_wear,
    analyze_time_of_day,
    analyze_occasions,
    analyze_mentioned_fragrances,
    analyze_performance,
    analyze_gender,
    analyze_summary,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FragranceAnalyzer:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API key is required")
        # Store the API key
        self.api_key = api_key
        logger.info("FragranceAnalyzer initialized")
        self._executor = ThreadPoolExecutor(
            max_workers=7
        )  # One worker per analysis type

    def merge_analyses(self, analyses):
        """Merge multiple analyses into one comprehensive analysis."""
        if not analyses:
            return None

        # Initialize the merged result with the first analysis
        merged = analyses[0]

        # Helper function to merge lists without duplicates while preserving order
        def merge_lists(lists):
            seen = set()
            merged = []
            for item in [x for sublist in lists for x in sublist]:
                if item not in seen:
                    seen.add(item)
                    merged.append(item)
            return merged

        # Helper function to merge mentioned fragrances
        def merge_fragrances(frag_lists):
            seen = {}
            merged = []
            for frag_list in frag_lists:
                for frag in frag_list:
                    name = frag["name"]
                    if name not in seen:
                        seen[name] = frag
                        merged.append(frag)
                    else:
                        # If this fragrance was mentioned in multiple chunks, combine the contexts
                        seen[name][
                            "context"
                        ] = f"{seen[name]['context']}. {frag['context']}"
            return merged

        # Merge all analyses
        for analysis in analyses[1:]:
            # Merge seasons
            merged["seasons"]["primary"] = merge_lists(
                [merged["seasons"]["primary"], analysis["seasons"]["primary"]]
            )
            merged["seasons"]["secondary"] = merge_lists(
                [merged["seasons"]["secondary"], analysis["seasons"]["secondary"]]
            )

            # Merge time of day
            merged["time_of_day"]["best_times"] = merge_lists(
                [
                    merged["time_of_day"]["best_times"],
                    analysis["time_of_day"]["best_times"],
                ]
            )

            # Merge occasions
            merged["occasions"] = merge_lists(
                [merged["occasions"], analysis["occasions"]]
            )

            # Merge mentioned fragrances
            merged["mentioned_fragrances"] = merge_fragrances(
                [merged["mentioned_fragrances"], analysis["mentioned_fragrances"]]
            )

        return merged

    async def analyze_reviews(self, reviews, fragrance_name):
        """Analyze reviews with progressive loading of results."""
        logger.info(f"Starting analysis for fragrance: {fragrance_name}")

        # Handle both string and list inputs
        if isinstance(reviews, list):
            logger.info(f"Total number of reviews: {len(reviews)}")
            # Take only first 20 reviews to avoid rate limits
            reviews = reviews[:20]
            combined_reviews = "\n".join([review["text"] for review in reviews])
            logger.info(f"Using first {len(reviews)} reviews for analysis")
        else:
            logger.info("Processing reviews as string")
            # Split the string into reviews and take first 20
            review_list = reviews.split("\n")
            review_list = review_list[:20]
            combined_reviews = "\n".join(review_list)
            logger.info(f"Using first {len(review_list)} reviews for analysis")

        # Create tasks for each analysis type
        analysis_tasks = [
            (
                "seasons",
                self._executor.submit(
                    analyze_seasonal_wear,
                    combined_reviews,
                    fragrance_name,
                    self.api_key,
                ),
            ),
            (
                "time_of_day",
                self._executor.submit(
                    analyze_time_of_day,
                    combined_reviews,
                    fragrance_name,
                    self.api_key,
                ),
            ),
            (
                "occasions",
                self._executor.submit(
                    analyze_occasions, combined_reviews, fragrance_name, self.api_key
                ),
            ),
            (
                "mentioned_fragrances",
                self._executor.submit(
                    analyze_mentioned_fragrances,
                    combined_reviews,
                    fragrance_name,
                    self.api_key,
                ),
            ),
            (
                "performance",
                self._executor.submit(
                    analyze_performance,
                    combined_reviews,
                    fragrance_name,
                    self.api_key,
                ),
            ),
            (
                "gender_classification",
                self._executor.submit(
                    analyze_gender, combined_reviews, fragrance_name, self.api_key
                ),
            ),
        ]

        # Initialize the result dictionary
        result = {}

        try:
            # Process each analysis as it completes
            for section_name, future in analysis_tasks:
                try:
                    section_result = future.result()
                    result[section_name] = section_result
                    # Emit progress update (you'll need to implement the WebSocket or SSE mechanism)
                    logger.info(f"Completed analysis section: {section_name}")
                except Exception as e:
                    logger.error(f"Error in {section_name} analysis: {str(e)}")
                    result[section_name] = {"error": str(e)}

            # Generate summary last, using the collected analysis
            try:
                summary_result = analyze_summary(
                    combined_reviews, fragrance_name, self.api_key
                )
                result["summary"] = summary_result["summary"]
            except Exception as e:
                logger.error(f"Error generating summary: {str(e)}")
                result["summary"] = f"Error generating summary: {str(e)}"

            logger.info("Successfully completed all analyses")
            return result

        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            return {
                "error": "Failed to analyze reviews. Please try again.",
                "details": str(e),
            }

    def __del__(self):
        self._executor.shutdown(wait=False)
