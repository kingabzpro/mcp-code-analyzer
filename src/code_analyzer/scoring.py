import json
import os
from typing import Dict, Any

from anthropic import Anthropic
from mistralai import Mistral
from openai import OpenAI
from pydantic import BaseModel, ValidationError

# ------------------------------------------------------------------ #
# Configuration
# ------------------------------------------------------------------ #

DEFAULT_SCORES: Dict[str, Any] = {
    "vulnerability_score": 0,
    "style_score": 0,
    "quality_score": 0,
}

ANALYSIS_PROMPT_TEMPLATE = (
    "Analyze the following code for vulnerabilities, style, and quality "
    "and return **only** a JSON object with keys "
    "'vulnerability_score', 'style_score', and 'quality_score' "
    "(each 0–100):\n```python\n{code}\n```"
)

SYSTEM_MESSAGES = {
    "anthropic": "You are a secure-coding assistant. Assess code quality, style and vulnerabilities.",
    "mistral": "You are a secure-coding assistant. Assess code quality, style and vulnerabilities.",
    "openai": "You are a secure-coding assistant. Assess code quality, style and vulnerabilities.",
}

MODELS = {
    "anthropic": "claude-opus-4-20250514",  # adjust if you use a different Claude-3 variant
    "mistral": "mistral-medium-2505",
    "openai": "gpt-4.1-2025-04-14",
}

REQUIRED_KEYS = ("vulnerability_score", "style_score", "quality_score")

# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #


class CodeAnalysisResult(BaseModel):
    vulnerability_score: int
    style_score: int
    quality_score: int


def _safe_json_loads(raw: str) -> Dict[str, Any]:
    """
    Best-effort JSON parsing – fall back to DEFAULT_SCORES on failure.
    """
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return DEFAULT_SCORES.copy()

def _ensure_all_keys(d: dict, default: int = 0) -> dict:
    """
    Return a dict that has every REQUIRED_KEYS entry.
    Missing keys are added with `default`.
    Non-required keys are discarded.
    """
    return {key: int(d.get(key, default)) for key in REQUIRED_KEYS}

# ------------------------------------------------------------------ #
# Provider wrappers
# ------------------------------------------------------------------ #


def analyze_code_anthropic(code: str) -> dict:
    if not code:
        return _ensure_all_keys({})

    try:
        client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(code=code)

        tools = [
            {
                "name": "code_scores",
                "description": "Return ONLY the three integer scores (0-100).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "vulnerability_score": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                        },
                        "style_score": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                        },
                        "quality_score": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                        },
                    },
                    "required": list(REQUIRED_KEYS),
                    "additionalProperties": False,
                },
            }
        ]

        resp = client.messages.create(
            model=MODELS["anthropic"],
            messages=[{"role": "user", "content": prompt}],
            system=SYSTEM_MESSAGES["anthropic"],
            tools=tools,
            tool_choice={"type": "tool", "name": "code_scores"},
            max_tokens=130,
            temperature=0,
        )

        tool_call = next(c for c in resp.content if c.type == "tool_use")
        return _ensure_all_keys(tool_call.input)

    except Exception as exc:
        out = _ensure_all_keys({})
        out["error"] = f"Anthropic API error: {exc}"
        return out

def analyze_code_mistral(code: str) -> Dict[str, Any]:
    if not code:
        return DEFAULT_SCORES.copy()

    try:
        client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(code=code)

        resp = client.chat.complete(
            model=MODELS["mistral"],
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGES["mistral"]},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        return _safe_json_loads(resp.choices[0].message.content)

    except Exception as exc:
        result = DEFAULT_SCORES.copy()
        result["error"] = f"Mistral API error: {exc}"
        return result


def analyze_code_openai(code: str) -> Dict[str, Any]:
    if not code:
        return DEFAULT_SCORES.copy()

    try:
        client = OpenAI()  # uses OPENAI_API_KEY from env
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(code=code)

        resp = client.chat.completions.create(
            model=MODELS["openai"],
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGES["openai"]},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        # Validate via Pydantic (optional but nice)
        parsed = _safe_json_loads(resp.choices[0].message.content)
        try:
            validated = CodeAnalysisResult(**parsed)
            return validated.model_dump()
        except ValidationError:
            # If model returns extra fields or wrong types, fall back to raw
            return parsed

    except Exception as exc:
        result = DEFAULT_SCORES.copy()
        result["error"] = f"OpenAI API error: {exc}"
        return result


# ------------------------------------------------------------------ #
# Aggregator
# ------------------------------------------------------------------ #


def create_code_score(code: str) -> Dict[str, Any]:
    if not code:
        return DEFAULT_SCORES.copy()

    scores_list = [
        analyze_code_anthropic(code),
        analyze_code_mistral(code),
        analyze_code_openai(code),
    ]
    valid = [s for s in scores_list if "error" not in s]

    if not valid:
        result = DEFAULT_SCORES.copy()
        result["error"] = "All API providers failed"
        return result

    # Average
    averaged = {
        "vulnerability_score": sum(s["vulnerability_score"] for s in valid)
        // len(valid),
        "style_score": sum(s["style_score"] for s in valid) // len(valid),
        "quality_score": sum(s["quality_score"] for s in valid) // len(valid),
    }
    return averaged


# ------------------------------------------------------------------ #
# Demo / quick test
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    sample = """
def example_function(x):
    if x is None:
        return "Error"
    return x * 2
"""

    print("Anthropic →", analyze_code_anthropic(sample))
    print("Mistral   →", analyze_code_mistral(sample))
    print("OpenAI    →", analyze_code_openai(sample))
    print("AVERAGED  →", create_code_score(sample))
