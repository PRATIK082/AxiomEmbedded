# AxiomEmbedded reproducible environment
FROM python:3.11-slim

LABEL org.opencontainers.image.title="AxiomEmbedded"
LABEL org.opencontainers.image.description="Open AI-Native Engineering Platform for Embedded & Cyber-Physical Systems"
LABEL org.opencontainers.image.license="Apache-2.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app

# Install Python package + test deps
RUN pip install --no-cache-dir -e '.[test]'

# Default command
CMD ["python", "-m", "axiom_cli", "doctor", "--skip-tests"]
