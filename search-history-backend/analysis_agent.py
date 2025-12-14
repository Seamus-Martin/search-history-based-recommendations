from openai import OpenAI
import json
import re

client = OpenAI()
MAX_CHARS = 6000


def _extract_json(text: str) -> dict:
   
    text = text.strip()

    # Remove ```json or ``` wrappers
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    return json.loads(text)

#This agent is used to analyze each website that is viewed by the user
def analyze_page(text: str, title: str, url: str) -> dict:
    response = client.responses.create(
        model="gpt-4o-mini",
        input=f"""
You are analyzing a webpage a user visited.

Title: {title}
URL: {url}

Content:
{text[:MAX_CHARS]}

Return ONLY valid JSON.
Do NOT wrap the response in markdown.
Do NOT include backticks.

Schema:
{{
  "main_topic": string,
  "user_intent": "learning" | "shopping" | "research" | "troubleshooting" | "news" | "other",
  "key_entities": string[],
  "concise_summary": string
}}
"""
    )

    content = response.output_text

    try:
        return _extract_json(content)
    except Exception as e:
        print("Invalid JSON from model:")
        print(content)
        return {}
