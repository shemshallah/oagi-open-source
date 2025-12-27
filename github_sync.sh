#!/bin/bash
# OAGI GitHub Sync Script
# Maintains bidirectional sync with GitHub repository

REPO_DIR="/oagi/repo"
GITHUB_REPO="git@github.com:shemshallah/oagi-open-source.git"
BRANCH="claude/exec-oagi-code-CUyKv"

cd $REPO_DIR

# Fetch latest
git fetch origin $BRANCH

# Check for remote changes
UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")

if [ $LOCAL != $REMOTE ]; then
    echo "🔄 Syncing with remote..."
    git pull origin $BRANCH
fi

# Push any local changes
if [ -n "$(git status --porcelain)" ]; then
    echo "📤 Pushing local changes..."
    git add -A
    git commit -m "OAGI autonomous update: $(date -Iseconds)"
    git push origin $BRANCH
fi

echo "✅ Sync complete"
