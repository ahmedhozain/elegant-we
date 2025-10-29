#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setting up database..."
# Initialize database if it doesn't exist
if [ ! -f website_content.db ]; then
    echo "Creating new database..."
    python migrate_database.py
else
    echo "Database already exists"
fi

echo "Build completed successfully!"

