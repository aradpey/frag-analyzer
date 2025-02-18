import openai
import json
import logging
import time

logger = logging.getLogger(__name__)


def analyze_occasions(reviews_text: str, fragrance_name: str, api_key: str) -> dict:
    """Analyze the suitable occasions for wearing the fragrance."""
    start_time = time.time()
    logger.info(f"Starting occasions analysis for {fragrance_name}")

    prompt = f"""Analyze these reviews for the fragrance '{fragrance_name}' and determine suitable occasions.
    Focus only on occasions and settings where the fragrance is recommended. Return in this JSON format:

    {{
        "occasions": ["List of occasions mentioned, capitalize each (e.g., Office, Date Night, Formal Events)"]
    }}

    IMPORTANT:
    1. Only include occasions explicitly mentioned or strongly implied in reviews
    2. Be specific but concise (e.g., "Formal Events" rather than just "Formal")
    3. Don't make assumptions about occasions not mentioned
    4. Include both social settings and specific events
    5. Common occasions to look for: Office, Work, Date Night, Casual Outings, Formal Events, Special Occasions, etc.

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
        logger.error(f"Error in occasions analysis: {str(e)}")
        return {"occasions": [], "error": str(e)}
