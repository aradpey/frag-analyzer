import openai
import json
import logging
import time

logger = logging.getLogger(__name__)


def analyze_time_of_day(reviews_text: str, fragrance_name: str, api_key: str) -> dict:
    """Analyze the optimal time of day for wearing the fragrance."""
    start_time = time.time()
    logger.info(f"Starting time of day analysis for {fragrance_name}")

    prompt = f"""Analyze these reviews for the fragrance '{fragrance_name}' and determine when it's best worn during the day.
    Focus only on time of day preferences. Return in this JSON format:

    {{
        "best_times": ["List of optimal times to wear, capitalize each (e.g., Morning, Day, Evening, Night)"],
        "versatility": "Describe time versatility using ONLY one of these terms: Extremely Versatile, Very Versatile, Moderately Versatile, Somewhat Limited, Very Limited, Specific Time Only"
    }}

    IMPORTANT:
    1. Only include times explicitly mentioned or strongly implied in reviews
    2. Best times should be those most frequently or strongly recommended
    3. Versatility should reflect how flexible the fragrance is across different times
    4. If a time isn't mentioned, don't include it
    5. Use only: Morning, Day, Afternoon, Evening, Night

    Reviews to analyze:

    {reviews_text}
    """

    try:
        # Set the API key
        openai.api_key = api_key

        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a perfume critic. Respond in JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            presence_penalty=0,
            frequency_penalty=0,
        )

        content = response.choices[0].message.content.strip()

        # Strip markdown code blocks if present
        if content.startswith("```json"):
            content = content.replace("```json", "", 1)
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        parsed_content = json.loads(content)
        return parsed_content

    except Exception as e:
        logger.error(f"Error in time of day analysis: {str(e)}")
        return {"best_times": [], "versatility": "Unknown", "error": str(e)}
