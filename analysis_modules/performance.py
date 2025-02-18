import openai
import json
import logging
import time

logger = logging.getLogger(__name__)


def analyze_performance(reviews_text: str, fragrance_name: str, api_key: str) -> dict:
    """Analyze the performance characteristics of the fragrance."""
    start_time = time.time()
    logger.info(f"Starting performance analysis for {fragrance_name}")

    prompt = f"""Analyze these reviews for the fragrance '{fragrance_name}' and evaluate its performance characteristics.
    Focus on longevity, sillage, and projection. Return in this JSON format:

    {{
        "longevity": {{
            "conclusion": "Duration in hours, be specific (e.g., 6-8 hours, 2-3 hours)",
            "analysis": "Brief explanation based on review consensus about longevity"
        }},
        "sillage": {{
            "conclusion": "One of: Enormous, Very Strong, Strong, Moderate, Soft, Very Soft, Intimate",
            "analysis": "Brief explanation of sillage based on reviews"
        }},
        "projection": {{
            "conclusion": "One of: Beast Mode, Strong Projector, Good Projection, Moderate Projection, Subtle Projection, Skin Scent",
            "analysis": "Brief explanation of projection based on reviews"
        }}
    }}

    IMPORTANT:
    1. Base conclusions only on information from reviews
    2. Use specific hour ranges for longevity when mentioned
    3. Consider consensus and varying experiences
    4. Keep analysis explanations brief but informative
    5. Use only the specified terms for sillage and projection conclusions

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
        logger.error(f"Error in performance analysis: {str(e)}")
        return {
            "longevity": {"conclusion": "Unknown", "analysis": "Error occurred"},
            "sillage": {"conclusion": "Unknown", "analysis": "Error occurred"},
            "projection": {"conclusion": "Unknown", "analysis": "Error occurred"},
            "error": str(e),
        }
