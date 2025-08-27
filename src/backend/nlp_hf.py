
from typing import Optional, List, Dict, Any
try:
    from transformers import pipeline
except Exception as e:
    pipeline = None
    _import_error = e

_SUMMARIZER = None

def get_summarizer():
    global _SUMMARIZER
    if _SUMMARIZER is not None:
        return _SUMMARIZER
    if pipeline is None:
        return None
    # Lightweight summarization model
    try:
        _SUMMARIZER = pipeline('summarization', model='sshleifer/distilbart-cnn-12-6')
        return _SUMMARIZER
    except Exception:
        # As a fallback, try t5-small
        try:
            _SUMMARIZER = pipeline('summarization', model='t5-small')
            return _SUMMARIZER
        except Exception:
            return None

def summarize_events(events: List[Dict[str, Any]], max_events: int = 12) -> str:
    if not events:
        return "No events available."
    texts = [f"{e.get('event_type','disaster')}: {e.get('title','')} in {e.get('country') or ''} at {e.get('start_time') or ''}." for e in events[:max_events]]
    joined = " ".join(texts)
    summarizer = get_summarizer()
    if summarizer is None:
        # Fallback: simple truncation
        return "\n".join(texts[:8])
    out = summarizer(joined, max_length=120, min_length=40, do_sample=False)
    return out[0]['summary_text']
