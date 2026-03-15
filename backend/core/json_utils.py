import json
import re
from typing import Any, Dict
from langchain_core.utils.json import parse_json_markdown

def clean_and_parse_json(content: Any) -> Dict[str, Any]:
    """
    Robustly parses JSON from LLM responses.
    Handles:
    1. Content as List (concatenates text parts)
    2. Markdown code blocks (```json ... ```)
    3. Text before/after the JSON block
    4. Missing commas between fields/elements
    5. Literal control characters (strict=False)
    6. Malformed JSON (via parse_json_markdown fallback)
    """
    if not content:
        return {}

    # 1. Handle list content (LangChain/Anthropic style)
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
            else:
                text_parts.append(str(part))
        content = "".join(text_parts)
    
    if not isinstance(content, str):
        content = str(content)

    # 2. Strip whitespace and markdown wrappers
    content = content.strip()
    
    # Extract JSON block using regex if present
    match = re.search(r'(\{.*\})', content, re.DOTALL)
    if match:
        content = match.group(1).strip()
    else:
        # If no braces found, maybe it's still markdown-wrapped?
        if content.startswith("```"):
            content = re.sub(r'^```(json)?', '', content).strip()
            content = re.sub(r'```$', '', content).strip()

    # 3. Aggressively fix common LLM JSON syntax errors
    # Fix missing commas between fields: "val" "key" -> "val", "key"
    content = re.sub(r'"\s*"', '", "', content)
    # Fix missing commas between objects/arrays: } " -> }, "
    content = re.sub(r'\}\s*"', '}, "', content)
    content = re.sub(r'\]\s*"', '], "', content)
    # Fix missing commas between numeric values and keys: 123 "key" -> 123, "key"
    content = re.sub(r'(\d+)\s*"', r'\1, "', content)

    # 4. Try standard JSON load with strict=False
    try:
        return json.loads(content, strict=False)
    except json.JSONDecodeError:
        pass

    # 5. Fallback to LangChain's robust parser
    try:
        return parse_json_markdown(content)
    except Exception as e:
        print(f"JSON Parsing fully failed: {e}")
        raise
