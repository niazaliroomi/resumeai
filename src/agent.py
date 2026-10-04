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


class ResumeAgent:
    def __init__(self, resume_text: str):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.resume_text = resume_text
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Here is my resume:\n\n{resume_text}"},
        ]

    def chat(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=self.messages,
            tools=TOOL_SCHEMAS,
        )

        # Agentic loop: keep going while the model wants to use tools
        while response.choices[0].message.tool_calls:
            message = response.choices[0].message
            self.messages.append(message.model_dump())

            for tool_call in message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                result = run_tool(tool_call.function.name, args, self.resume_text)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=self.messages,
                tools=TOOL_SCHEMAS,
            )

        final_message = response.choices[0].message
        self.messages.append(final_message.model_dump())
        return final_message.content
