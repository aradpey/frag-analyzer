import openai
import json
import logging

logger = logging.getLogger(__name__)


def analyze_seasonal_wear(reviews_text: str, fragrance_name: str, api_key: str) -> dict:
    """Analyze the seasonal wear characteristics of a fragrance."""
    logger.info(f"Starting seasonal wear analysis for {fragrance_name}")

    prompt = f"""Analyze these reviews for the fragrance '{fragrance_name}' and determine its seasonal characteristics.
    Focus only on when the fragrance is best worn in terms of seasons. Return in this JSON format:

    {{
        "primary": ["List of main seasons this fragrance is best for, capitalize each season"],
        "secondary": ["List of seasons it can also work in, capitalize each season"]
    }}

    IMPORTANT:
    1. Only include seasons explicitly mentioned or strongly implied in the reviews
    2. Primary seasons should be those most frequently or strongly recommended
    3. Secondary seasons should be those mentioned as acceptable but not ideal
    4. If a season isn't mentioned at all, don't include it
    5. Use only: Spring, Summer, Fall, Winter

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
        logger.error(f"Error in seasonal wear analysis: {str(e)}")
        return {"primary": [], "secondary": [], "error": str(e)}
