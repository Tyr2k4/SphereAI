# Security Policy

## Reporting a concern

This is a small personal/portfolio project. If you spot a security issue, please open
a GitHub issue or contact the maintainer directly rather than exploiting it — see the
contact details in the main [README](README.md).

## Known risk: FAISS index deserialization

`app.py` loads the local vector store with:

```python
FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
```

LangChain requires this flag because `FAISS.load_local` uses Python's `pickle` module
internally to restore the docstore. Unpickling data from an untrusted source can execute
arbitrary code — this is a general property of `pickle`, not a bug specific to FAISS.

**Why this is acceptable here:** `faiss_index/` is:
- listed in `.gitignore`, so it is never committed to the public repo,
- produced exclusively by running `build_brain.py` locally against `listings2.csv`,
- never downloaded from a third party or accepted as user input.

**When this would become dangerous:** if `faiss_index/` is ever sourced from anywhere
other than your own `build_brain.py` run — a contributor's PR, a shared drive, an
external download, an automated pipeline pulling from a bucket you don't fully
control — treat that as equivalent to running an untrusted `.pkl` file. Don't do it
without first verifying the source.

## Data source trust boundary

`listings2.csv` is embedded and later injected into every LLM prompt as retrieved
"Context" (see `build_brain.py` and the prompt template in `app.py`). Anyone who can
edit that CSV can influence what the assistant says, including attempting prompt
injection. Only populate it from your own vetted CRM/database export.

## Network egress

The app makes outbound requests to exactly one third-party service:
`generativelanguage.googleapis.com` (Google's Generative AI API, via
`langchain-google-genai` / `google-generativeai`). There is no other network client,
proxy, or URL-fetching tool in this codebase. If you deploy behind a firewall or
egress proxy, that is the only domain that needs to be allowed.

## Secrets

- All credentials are loaded from environment variables via `python-dotenv` — see
  `.env.example`. Never commit a real `.env` file.
- If you ever suspect a key has leaked (e.g. committed by accident, pasted somewhere
  public), revoke it immediately in [Google AI Studio](https://aistudio.google.com/)
  and issue a new one. A revoked key cannot be un-leaked, only replaced.
- Logs and UI error messages are scrubbed of API key patterns via `logging_utils.py`
  before being printed or displayed — see that file for details.
