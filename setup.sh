
#!/usr/bin/env bash
set -euo pipefail

PROJECT_VENV=".venv_disaster_event_chatbot"

python -m venv "${PROJECT_VENV}"
# shellcheck disable=SC1090
source "${PROJECT_VENV}/bin/activate"

python -m pip install --upgrade pip setuptools wheel

# Prefer binary wheel for pyarrow to avoid source builds
export PIP_ONLY_BINARY="pyarrow"

# Install CPU-only torch first to avoid GPU CUDA pulls on laptops
python -m pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision torchaudio || true

pip install -r requirements.txt

echo "✅ Virtualenv ready: ${PROJECT_VENV}"
echo "Run: source ${PROJECT_VENV}/bin/activate"
