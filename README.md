# RI-Experiment-LLM

This repository contains a simple Flask backend and a small React
frontend used to run a rational inattention experiment with an LLM agent
recommender.

## Setup

Install the python dependencies and start the backend:

```bash
pip install -r requirements.txt
python -m backend.app
```

The frontend is a minimal static bundle located in `frontend/`. Serve it
with any webserver or the built‑in Flask static file system.

## OpenAI API Key

Set the `OPENAI_API_KEY` environment variable before starting the backend.
If the key is not defined or starts with `sk-demo`, the backend will return
mock completions instead of calling the real API.

## Development

The backend exposes a REST API used by the browser client:

- `POST /start` – begin a session for a cost arm
- `POST /round/<round>` – start a new round
- `POST /prompt` – send a prompt to GPT‑4o (or a mock)
- `POST /choose` – record the product choice and return the payoff

Constants for the experiment are defined in `backend/constants.py`.
