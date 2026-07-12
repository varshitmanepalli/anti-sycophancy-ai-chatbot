#!/usr/bin/env bash
# Development helper scripts.
# Usage: ./scripts/dev.sh

set -euo pipefail

echo "Starting services with Docker Compose..."
docker compose up --build
