
PROJECT_VENV=.venv_disaster_event_chatbot

.PHONY: init dev api ui ingest test clean

init:
	python -m venv $(PROJECT_VENV)
	. $(PROJECT_VENV)/bin/activate && python -m pip install --upgrade pip setuptools wheel
	PIP_ONLY_BINARY=pyarrow . $(PROJECT_VENV)/bin/activate && pip install -r requirements.txt

dev:
	. $(PROJECT_VENV)/bin/activate && pre-commit install || true

api:
	. $(PROJECT_VENV)/bin/activate && uvicorn src.backend.main:app --reload --port 8000

ui:
	. $(PROJECT_VENV)/bin/activate && streamlit run src/app.py

ingest:
	. $(PROJECT_VENV)/bin/activate && python -m src.scripts.ingest_once

test:
	. $(PROJECT_VENV)/bin/activate && pytest -q

clean:
	rm -rf $(PROJECT_VENV) .pytest_cache __pycache__ */__pycache__ data/*.db
