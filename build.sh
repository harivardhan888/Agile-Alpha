#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Build Frontend
cd frontend
npm install
npm run build
cd ..

# Copy build to static for FastAPI to serve
rm -rf static
cp -r frontend/dist static
