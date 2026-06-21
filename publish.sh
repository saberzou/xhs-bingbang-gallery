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

# 1b. QA quality gate (Axiom) - scores the new draft + recent window against
#     the WORLD-BIBLE voice rules. Non-blocking: logs PASS/FAIL, never stops
#     publishing, but FAIL is recorded loudly so drift gets caught early.
TODAY=$(date +%Y-%m-%d)
echo "-> Running verify_quality.py (QA gate)..." >> "$LOG_FILE"
if python3 verify_quality.py --date "$TODAY" >> "$LOG_FILE" 2>&1; then
  echo "   QA: today PASS" >> "$LOG_FILE"
else
  echo "   QA: today FAIL  <-- caption drifted off-bible, review before posting" >> "$LOG_FILE"
fi
python3 verify_quality.py --window 14 >> "$LOG_FILE" 2>&1 || \
  echo "   QA: 14-day batch FAIL (cast/job/emotion/grounded drift) - see report above" >> "$LOG_FILE"

# 2. Build static site
echo "-> Running build_site.py..." >> "$LOG_FILE"
python3 build_site.py >> "$LOG_FILE" 2>&1

# 3. Commit and push
# Cron runs in a non-interactive shell that CANNOT reach the macOS keychain
# (osxkeychain helper), which is why the June 18/19 auto-pushes failed silently
# with "could not read Username for https://github.com". gh stores its token in
# its own keyring and `gh auth git-credential` serves it non-interactively, so
# we point git at that helper for this push instead of the keychain.
echo "-> Pushing to GitHub..." >> "$LOG_FILE"
git add drafts/ docs/ >> "$LOG_FILE" 2>&1
git commit -m "Auto-generate content for $(date +%Y-%m-%d)" >> "$LOG_FILE" 2>&1 || true # ignore error if nothing to commit
if git -c credential.helper='!gh auth git-credential' push origin main >> "$LOG_FILE" 2>&1; then
  echo "   PUSH: ok" >> "$LOG_FILE"
else
  # Do NOT swallow this. A silent push failure means the live feed is stale
  # while drafts/ keeps advancing locally. Make it loud so cron.log + the QA
  # watchdog surface it.
  echo "   PUSH: FAILED <-- live site is now STALE, commits stuck local. Check gh auth." >> "$LOG_FILE"
fi

echo "Done: $(date)" >> "$LOG_FILE"
