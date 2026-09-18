"""
Shared logging helper: scrubs secrets out of text before it's printed to the
console or shown in the UI. Exception messages from Google's API clients can
embed the request URL, which sometimes includes the API key as a query
parameter (e.g. "...?key=AIzaSy..."), so every place that logs an exception
should route it through scrub_secrets() first — never print(e) directly.
"""
import os
import re

# Matches Google API key format (AIza + 35 chars) wherever it appears.
_GOOGLE_KEY_PATTERN = re.compile(r"AIza[0-9A-Za-z\-_]{35}")
# Matches "key=<value>" query params some Google client errors embed in URLs.
_KEY_PARAM_PATTERN = re.compile(r"([?&]key=)[^&\s'\"]+")


def scrub_secrets(text: str) -> str:
    """Redact known API key patterns from a string. Safe to call on any text
    before logging it — returns the input unchanged if nothing matches."""
    if not text:
        return text
    text = str(text)
    text = _GOOGLE_KEY_PATTERN.sub("[REDACTED_API_KEY]", text)
    text = _KEY_PARAM_PATTERN.sub(r"\1[REDACTED]", text)
    # Belt-and-suspenders: also scrub the literal key currently loaded in env,
    # in case a future error message includes it in some other unexpected format.
    live_key = os.getenv("GOOGLE_API_KEY")
    if live_key:
        text = text.replace(live_key, "[REDACTED_API_KEY]")
    return text


def log_error(prefix: str, exc: Exception) -> str:
    """Print a scrubbed error to the console and return the scrubbed message,
    so callers can also show it in a UI without leaking secrets."""
    message = scrub_secrets(str(exc))
    print(f"{prefix}: {message}")
    return message
