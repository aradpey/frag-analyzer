import openai
import json
import logging
import time

logger = logging.getLogger(__name__)


def analyze_mentioned_fragrances(
    reviews_text: str, fragrance_name: str, api_key: str
) -> dict:
    """Analyze other fragrances mentioned in the reviews."""
    start_time = time.time()
    logger.info(f"Starting mentioned fragrances analysis for {fragrance_name}")

    prompt = f"""Analyze these reviews for the fragrance '{fragrance_name}' and identify other fragrances mentioned.
    Return in this JSON format:

    {{
        "mentioned_fragrances": [
            {{
                "name": "Name of mentioned fragrance",
                "context": "2-3 sentence explanation of the connection. Include: similarity level (if mentioned), shared notes or characteristics, and any key differences. Example: 'About 80% similar, sharing the same powdery iris base but with a sweeter vanilla in the top notes. More versatile than the original.'"
            }}
        ]
    }}

    IMPORTANT:
    1. Only include fragrances explicitly mentioned
    2. For each fragrance, provide:
       - How similar they are (percentage or descriptive)
       - What specific notes or characteristics they share
       - Key differences or unique aspects
       - Performance comparison (if mentioned)
    3. Keep explanations focused but informative (2-3 sentences)
    4. Focus on direct comparisons made in the reviews
    5. If no specific comparison is made, explain what aspect was mentioned

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
                    "content": "You are a perfume critic. Respond in JSON. Provide clear, informative comparisons.",
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
        logger.error(f"Error in mentioned fragrances analysis: {str(e)}")
        return {"mentioned_fragrances": [], "error": str(e)}
