import openai
import json
import logging
import time

logger = logging.getLogger(__name__)


def analyze_gender(reviews_text: str, fragrance_name: str, api_key: str) -> dict:
    """Analyze the gender classification and versatility of the fragrance."""
    start_time = time.time()
    logger.info(f"Starting gender analysis for {fragrance_name}")

    prompt = f"""Analyze these reviews for the fragrance '{fragrance_name}' and determine its gender characteristics.
    Focus on gender perception and versatility. Return in this JSON format:

    {{
        "primary": {{
            "conclusion": "One of: Distinctly Masculine, Predominantly Masculine, Slightly Masculine-Leaning, Truly Unisex, Slightly Feminine-Leaning, Predominantly Feminine, Distinctly Feminine",
            "analysis": "Brief explanation of gender classification based on reviews"
        }},
        "versatility": {{
            "conclusion": "One of: Universal Appeal, Highly Versatile, Adaptable, Somewhat Restricted, Traditional Gender-Specific",
            "analysis": "Brief explanation of gender versatility based on reviews"
        }}
    }}

    IMPORTANT:
    1. Base conclusions only on information from reviews
    2. Consider both explicit statements and implicit suggestions
    3. Note any disagreements or varying opinions
    4. Keep analysis explanations brief but informative
    5. Use only the specified terms for conclusions

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
        logger.error(f"Error in gender analysis: {str(e)}")
        return {
            "primary": {"conclusion": "Unknown", "analysis": "Error occurred"},
            "versatility": {"conclusion": "Unknown", "analysis": "Error occurred"},
            "error": str(e),
        }
