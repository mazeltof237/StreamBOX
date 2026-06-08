#!/usr/bin/env bash
# Build script pour Render (backend Django).
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input
python manage.py seed_data || true
