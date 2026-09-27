# Text-to-SQL Agent

A portable, natural-language-to-SQL agent built with LangChain, designed to plug into different SQL databases with minimal changes. Built as a hands-on learning project in agentic engineering — going from first-principles understanding of agent components to a working implementation.

## Status
🚧 In progress — currently at Phase 4 (database setup) of the build.

## Tech Stack
- **Orchestration:** LangChain (built on LangGraph under the hood)
- **Model:** Google Gemini (`gemini-3.8-flash`), via `langchain-google-genai`
- **Database layer:** `SQLDatabase` utility (from `langchain-community`) + SQLAlchemy, for portability across SQL engines
- **Sample dataset:** [Chinook](https://github.com/lerocha/chinook-database) — a sample digital media store database (SQLite)

## Why Gemini
Chosen for its genuinely free tier (rate-limited, not credit-limited) — useful for an iterative, debugging-heavy build like this one. The model provider is swappable via one config line (`init_chat_model`'s `model_provider` argument), so this isn't a hard dependency on Google specifically.

## A note on `langchain-community`
As of this project's build, `langchain-community` has been officially sunset (repo archived, no further fixes). However, `SQLDatabase` and `SQLDatabaseToolkit` — the core utilities this project relies on for schema introspection and portable DB connections — currently have **no successor package**; `langchain_classic` only re-exports the same (deprecated) code path. Both available import paths emit deprecation warnings that point at each other. This project uses `langchain_community.utilities.SQLDatabase` deliberately, with the dependency version pinned in `requirements.txt`, until the ecosystem settles on a stable successor.

## Setup

### 1. Clone and create a virtual environment
\`\`\`bash
git clone https://github.com/suhaspadi-work/text-to-sql-agent.git
cd text-to-sql-agent
python3 -m venv .venv
source .venv/bin/activate
\`\`\`

### 2. Install dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. Set up environment variables
Create a `.env` file in the project root with:
\`\`\`
GOOGLE_API_KEY=your_google_api_key_here
DATABASE_URL=sqlite:///chinook.db
\`\`\`
Get a free Gemini API key at https://aistudio.google.com/apikey.

### 4. Download the sample database
\`\`\`bash
python -c "
import requests, pathlib
url = 'https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db'
pathlib.Path('chinook.db').write_bytes(requests.get(url).content)
"
\`\`\`

### 5. Verify setup
\`\`\`bash
python test_connection.py
\`\`\`
Should print a response from the Gemini model, confirming your API key and dependencies are working.

## Design principles
- **Portability first:** database connection is config-driven (`DATABASE_URL`), not hardcoded — swapping to Postgres/MySQL later should require no code changes, only a connection string and driver.
- **Safety-scoped:** database access is intended to be read-only; a human-in-the-loop review step gates any potentially destructive query.

## Roadmap
- [x] Environment + git setup
- [x] Core dependencies installed
- [x] Model connectivity verified (Gemini)
- [x] Sample database (Chinook) downloaded and verified
- [ ] Schema introspection tools wired up
- [ ] SQL agent assembled (query tool + schema tool + model)
- [ ] Human-in-the-loop safety gate verified
- [ ] Custom evaluation set built and run
- [ ] Deliberate stress-testing (ambiguous questions, error recovery)
- [ ] Tested against a second database engine (portability validation)