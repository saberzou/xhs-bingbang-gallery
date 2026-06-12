#!/bin/bash
# Cron job script to generate content, build site, and push to GitHub
set -e

# Ensure /opt/homebrew/bin (and friends) are on PATH so the script can call
# openclaw / git / etc. when launched from a bare cron context.
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# Configuration
REPO_DIR="/Users/saberzou/.openclaw/workspace-axel/projects/xhs-creator"
LOG_FILE="$REPO_DIR/cron.log"

echo "======================================" >> "$LOG_FILE"
echo "Starting Daily XHS Job: $(date)" >> "$LOG_FILE"

cd "$REPO_DIR"

# 1. Generate new content
echo "-> Running generate.py..." >> "$LOG_FILE"
python3 generate.py >> "$LOG_FILE" 2>&1

# 2. Build static site
echo "-> Running build_site.py..." >> "$LOG_FILE"
python3 build_site.py >> "$LOG_FILE" 2>&1

# 3. Commit and push
echo "-> Pushing to GitHub..." >> "$LOG_FILE"
git add drafts/ docs/ >> "$LOG_FILE" 2>&1
git commit -m "Auto-generate content for $(date +%Y-%m-%d)" >> "$LOG_FILE" 2>&1 || true # ignore error if nothing to commit
git push origin main >> "$LOG_FILE" 2>&1 || true

echo "Done: $(date)" >> "$LOG_FILE"
