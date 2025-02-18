import openai
import json
import logging
import time

logger = logging.getLogger(__name__)


def analyze_summary(reviews_text: str, fragrance_name: str, api_key: str) -> dict:
    """Create a concise summary of the fragrance based on reviews."""
    start_time = time.time()
    logger.info(f"Starting summary analysis for {fragrance_name}")

    prompt = f"""Create a brief summary for the fragrance '{fragrance_name}' based on these reviews.
    Focus on the most important and distinctive characteristics. Return in this JSON format:

    {{
        "summary": "2-3 sentence overall impression. Ensure proper capitalization."
    }}

    IMPORTANT:
    1. Highlight the most distinctive features
    2. Include key strengths and any notable limitations
    3. Mention performance if it's a significant factor
    4. Keep to 2-3 concise but informative sentences
    5. Use proper grammar and capitalization

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
        logger.error(f"Error in summary analysis: {str(e)}")
        return {"summary": "Error occurred while generating summary.", "error": str(e)}
