# 🏠 SphereAI

SphereAI is an AI-powered chat assistant for a real estate company (Homesphere Real
Estate LLC). It answers visitor questions about property listings — availability,
pricing, features — by retrieving relevant listings from a local knowledge base and
generating grounded answers with Google's Gemini models.

Built with [Streamlit](https://streamlit.io/), [LangChain](https://www.langchain.com/),
Google's Generative AI API, and a local [FAISS](https://github.com/facebookresearch/faiss)
vector index.

## How it works

1. **`build_brain.py`** reads property listings from a CSV file, embeds each row using
   Google's embedding model, and saves the result as a local FAISS vector index
   (`faiss_index/`) — this is the assistant's "knowledge base."
2. **`app.py`** is the Streamlit chat interface. When a visitor asks a question, it
   retrieves the most relevant listings from the FAISS index, combines them with chat
   history, and asks Gemini to answer using only that context.
3. **`check_models.py`**, **`check_embeddings.py`**, **`find_working_model.py`** are
   small diagnostic scripts for confirming which Gemini models/embedding models are
   available and working on your API key — useful when Google adds, renames, or
   deprecates models.

## Project structure

```
.
├── app.py                  # Streamlit chat app (the assistant itself)
├── build_brain.py          # Builds the FAISS vector index from listings2.csv
├── check_models.py         # Lists available Gemini chat models for your API key
├── check_embeddings.py     # Lists available Gemini embedding models for your API key
├── find_working_model.py   # Finds and tests a working embedding model automatically
├── logging_utils.py        # Shared helper that scrubs secrets from logs/errors
├── requirements.txt
├── .env.example             # Copy to .env and fill in your own key
├── .gitignore
├── SECURITY.md              # Security policy and known-risk details
└── listings2.csv            # Your property data (not included — see below)
```

## Prerequisites

- Python 3.9+
- A Google AI Studio API key ([aistudio.google.com](https://aistudio.google.com/))
- A `listings2.csv` file with your property data, including a `Project Name` column

## Setup

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd <your-repo-name>

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
cp .env.example .env
# then open .env and paste your real Google API key

# 5. Add your data
# Place your listings2.csv (with a "Project Name" column) in the project root
```

## Usage

**Build the knowledge base** (run once, and again any time your listings change):

```bash
python build_brain.py
```

This processes your CSV one row at a time with automatic retry/backoff on rate limits,
and saves the result to `faiss_index/`.

**Run the assistant:**

```bash
streamlit run app.py
```

Then open the local URL Streamlit prints (typically `http://localhost:8501`).

**Diagnose model access issues**, if `build_brain.py` or `app.py` errors out on model
names:

```bash
python check_models.py          # chat models available to your key
python check_embeddings.py      # embedding models available to your key
python find_working_model.py    # auto-finds and tests a working embedding model
```

## Security considerations

This project has been reviewed and hardened for public-repo exposure:

- **Secrets management** — no API keys are hardcoded anywhere in the codebase. All
  scripts load `GOOGLE_API_KEY` from environment variables via `python-dotenv`.
  `.env` is git-ignored; `.env.example` ships with a dummy placeholder only. If a real
  key is ever exposed (e.g. committed by accident), revoke it immediately in
  [Google AI Studio](https://aistudio.google.com/) — a leaked key should be treated as
  permanently compromised.
- **Code execution** — no `eval()`, `exec()`, `os.system()`, or shell calls anywhere in
  this codebase.
- **Deserialization** — the FAISS index is loaded with `allow_dangerous_deserialization=True`,
  which enables `pickle`-based loading. This is safe only because `faiss_index/` is
  never committed and is always produced locally by `build_brain.py`. See
  [`SECURITY.md`](SECURITY.md) for the full explanation and threat boundary.
- **Input validation / prompt injection** — user chat input is length-capped and
  stripped of non-printable characters before use. More importantly, the LLM prompt
  template explicitly instructs the model to treat retrieved `Context` and
  `Chat History` as reference data only, never as instructions — guarding against both
  live user injection attempts and injection via poisoned listing data.
- **Data source trust** — `listings2.csv` is embedded into every prompt as context, so
  it should only ever be populated from your own vetted CRM/database export, not an
  externally-editable feed.
- **Tool / file system sandboxing** — all file reads/writes are confined to the
  project directory via a `safe_path()` helper, preventing path traversal if these
  paths are ever made configurable in the future. The app makes network requests to
  exactly one destination, Google's Generative AI API — there is no other network
  client or URL-fetching tool in the codebase.
- **Logging** — all exception messages are passed through `logging_utils.scrub_secrets()`
  before being printed or shown in the UI, redacting API keys even if they appear
  embedded in an error message or request URL. End users of the deployed app see
  generic error messages, never raw exception detail.

Full details and the reasoning behind each of these live in [`SECURITY.md`](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).
