"""
ResumeAgent: a minimal agentic loop built on Groq's tool calling.

How it works:
1. Send the conversation + available tools to Groq.
2. If Groq asks to call tools -> run them, send results back, repeat.
3. When Groq stops calling tools -> return the final answer.
"""
import json
from groq import Groq

from src.config import GROQ_API_KEY, MODEL_NAME
from src.prompts import SYSTEM_PROMPT
from src.tools import TOOL_SCHEMAS, run_tool


def _clean_message(m):
    """Groq strictly validates message format, so we keep only
    the fields it needs and never send 'content: None'."""
    if hasattr(m, "model_dump"):   # convert SDK message object -> dict
        m = m.model_dump()
    cleaned = {"role": m["role"], "content": m.get("content") or ""}
    if m.get("tool_calls"):
        cleaned["tool_calls"] = [
            {
                "id": tc["id"],
                "type": "function",
                "function": {
                    "name": tc["function"]["name"],
                    "arguments": tc["function"]["arguments"],
                },
            }
            for tc in m["tool_calls"]
        ]
    if m["role"] == "tool":
        cleaned["tool_call_id"] = m["tool_call_id"]
    return cleaned


class ResumeAgent:
    def __init__(self, resume_text: str):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.resume_text = resume_text
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Here is my resume:\n\n{resume_text}"},
        ]

    def _ask(self):
        """Send the cleaned conversation to Groq."""
        return self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[_clean_message(m) for m in self.messages],
            tools=TOOL_SCHEMAS,
        )

    def chat(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})

        response = self._ask()

        # Agentic loop: keep going while the model wants to use tools
        while response.choices[0].message.tool_calls:
            self.messages.append(response.choices[0].message)

            for tool_call in response.choices[0].message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                result = run_tool(tool_call.function.name, args, self.resume_text)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            response = self._ask()

        final_message = response.choices[0].message
        self.messages.append(final_message)
        return final_message.content
