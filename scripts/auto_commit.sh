#!/bin/bash

# Auto-commit script for smoke detection system
# Usage: ./scripts/auto_commit.sh "Your commit message"

# Check if commit message is provided
if [ -z "$1" ]; then
    echo "Usage: $0 \"Your commit message\""
    exit 1
fi

COMMIT_MESSAGE="$1"

# Check if there are any changes
if git diff-index --quiet HEAD --; then
    echo "No changes to commit"
    exit 0
fi

# Add all changes
git add .

# Commit with timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
FULL_MESSAGE="[AUTO] $COMMIT_MESSAGE - $TIMESTAMP"

echo "Committing changes: $FULL_MESSAGE"
git commit -m "$FULL_MESSAGE"

# Push to remote if origin is configured
if git remote get-url origin > /dev/null 2>&1; then
    echo "Pushing to remote repository..."
    git push origin main
else
    echo "No remote repository configured. Skipping push."
fi

echo "Auto-commit completed successfully!" 