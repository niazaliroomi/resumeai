"""
Agent tools: plain Python functions + the JSON schemas the LLM uses to call them.
Adding a new tool = write a function here + add its schema to TOOL_SCHEMAS.
"""
import re

# ---------- tool implementations ----------


def word_count(resume_text: str) -> dict:
    """Count words and characters in the resume."""
    words = re.findall(r"\b\w+\b", resume_text)
    return {"word_count": len(words), "char_count": len(resume_text)}


STOPWORDS = {
    "the", "and", "for", "with", "you", "your", "our", "are", "will",
    "have", "has", "that", "this", "from", "they", "them", "who", "what",
    "when", "where", "which", "their", "about", "into", "over", "under",
    "other", "than", "then", "them", "must", "should", "would", "could",
}


def match_keywords(resume_text: str, job_description: str, top_n: int = 25) -> dict:
    """Compare resume keywords against a job description."""
    def keywords(text):
        words = re.findall(r"[a-zA-Z][a-zA-Z+#.\-]*", text.lower())
        freq = {}
        for w in words:
            if len(w) > 3 and w not in STOPWORDS:
                freq[w] = freq.get(w, 0) + 1
        return freq

    jd_kw = keywords(job_description)
    resume_words = set(keywords(resume_text))

    important = sorted(jd_kw, key=jd_kw.get, reverse=True)[:top_n]
    matched = [w for w in important if w in resume_words]
    missing = [w for w in important if w not in resume_words]
    score = round(100 * len(matched) / len(important)) if important else 0

    return {
        "match_score_percent": score,
        "matched_keywords": matched,
        "missing_keywords": missing,
    }


def get_resume_text(resume_text: str) -> str:
    """Return the full resume text (use when you need to re-read details)."""
    return resume_text


# ---------- schemas the LLM sees ----------

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "word_count",
            "description": "Count words and characters in the user's resume.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "match_keywords",
            "description": "Compare the resume against a job description and report matched/missing keywords with a match score.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_description": {
                        "type": "string",
                        "description": "The full job description text.",
                    }
                },
                "required": ["job_description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_resume_text",
            "description": "Read the full resume text again.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def run_tool(name: str, arguments: dict, resume_text: str) -> str:
    """Dispatch a tool call to the right function."""
    if name == "word_count":
        return str(word_count(resume_text))
    if name == "match_keywords":
        return str(match_keywords(resume_text, arguments["job_description"]))
    if name == "get_resume_text":
        return str(get_resume_text(resume_text))
    return f"Unknown tool: {name}"
