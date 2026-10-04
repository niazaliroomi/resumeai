# 📄 Agentic Resume Assistant

A beginner-friendly, agentic AI resume coach built with **Streamlit + Groq**.
Upload your resume, then chat with an agent that can review it, rewrite weak
sections, score you against job descriptions, and write cover letters.

## ✨ Features
- 📂 Upload resume as PDF or TXT
- 🤖 Agentic loop: the LLM decides when to use tools (keyword matching, word counts, re-reading your resume)
- 🎯 Job description matching with a match score
- ✍️ Resume rewrites, summaries, and cover letters
- 🧱 Simple modular code — easy to extend with new tools

## 🗂️ Project structure
```
resume-assistant/
├── app.py               # Streamlit UI (frontend)
├── requirements.txt
├── .env.example         # copy to .env and add your key
├── src/
│   ├── config.py        # API keys & settings
│   ├── prompts.py       # system prompt (edit to change behavior)
│   ├── tools.py         # agent tools + tool schemas
│   ├── agent.py         # the agentic loop (Groq tool calling)
│   └── resume_loader.py # PDF/TXT text extraction
```

## 🚀 Run locally
```bash
# 1. clone and enter the folder
git clone <your-repo-url>
cd resume-assistant

# 2. create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. install dependencies
pip install -r requirements.txt

# 4. add your Groq API key
cp .env.example .env             # Windows: copy .env.example .env
# then edit .env and paste your key from https://console.groq.com/keys

# 5. run
streamlit run app.py
```

## ☁️ Deploy on Streamlit Community Cloud
1. Push this repo to GitHub (make sure `.env` is NOT committed — it's in `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → pick your repo.
3. In **Advanced settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   MODEL_NAME = "llama-3.3-70b-versatile"
   ```
   (Streamlit Cloud automatically loads `secrets.toml` into environment variables,
   which `python-dotenv` + `os.getenv` will pick up.)
4. Deploy! 🎉

## 🔧 Adding a new tool (example: count bullet points)
1. In `src/tools.py`, write the function:
   ```python
   def count_bullets(resume_text: str) -> int:
       return resume_text.count("•") + resume_text.count("- ")
   ```
2. Add its schema to `TOOL_SCHEMAS`.
3. Add a line in `run_tool` to dispatch it.

That's it — the agent will now use it on its own when relevant.

## 📝 Notes
- The keyword matcher is intentionally simple (no heavy NLP libs) — good enough
  for a beginner project and easy to upgrade later.
- Conversation history is kept in memory only; it resets when the app restarts.
