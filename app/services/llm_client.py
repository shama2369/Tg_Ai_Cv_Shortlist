from __future__ import annotations
import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

from openai import OpenAI

# Load environment variables
load_dotenv()


class LLMError(Exception):
    pass


def llm_extract_json(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    Calls OpenAI and forces strict JSON output.
    Uses the new OpenAI client API.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMError("OPENAI_API_KEY not set")

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # stable + cost-effective
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,   # deterministic extraction
            max_tokens=2000,   # Increased for larger responses
            response_format={"type": "json_object"},  # Force JSON output
        )

        if not response.choices or not response.choices[0].message:
            raise LLMError("Empty response from OpenAI API")
        
        content = response.choices[0].message.content
        if not content:
            raise LLMError("Empty content in OpenAI response")
        
        content = content.strip()
        
        # Log first 200 chars for debugging
        logger.debug(f"LLM response preview: {content[:200]}...")

        # Hard safety: must be JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # Log the actual response for debugging
            logger.error(f"Invalid JSON from LLM. Response: {content[:500]}")
            raise LLMError(f"LLM did not return valid JSON: {e}. Response preview: {content[:200]}")

    except json.JSONDecodeError as e:
        raise LLMError(f"LLM did not return valid JSON: {e}")

    except Exception as e:
        raise LLMError(f"OpenAI API error: {str(e)}")
