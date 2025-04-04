#!/bin/bash

echo "⚙️ BUILD START"

# Install dependencies
python3.9 -m pip install --upgrade pip
python3.9 -m pip install -r requirements.txt

# Collect static files into STATIC_ROOT
python3.9 manage.py collectstatic --noinput --clear

echo "✅ BUILD END"
