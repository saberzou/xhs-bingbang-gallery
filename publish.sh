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
# The system `cron` daemon (this script's launcher, `0 8 * * *`) runs in a
# non-interactive session that CANNOT unlock the macOS login keychain. Both the
# osxkeychain helper AND `gh auth git-credential` read gh's token from that
# keychain, so under cron they fail with "could not read Username" /
# "Device not configured" (this bit the June 18/19 AND June 23 auto-pushes).
#
# Fix: read the token from a 600-perm file OUTSIDE the repo that does NOT depend
# on the keychain at runtime. When the box IS interactive (manual run, agent
# session) we refresh that file from `gh auth token` so it never goes stale.
TOKEN_FILE="$HOME/.openclaw/secrets/gh-xhs-push.token"
PUSH_URL="https://x-access-token:TOKEN@github.com/saberzou/xhs-bingbang-gallery.git"

# Best-effort token refresh (only works when keychain is reachable; harmless under cron)
if command -v gh >/dev/null 2>&1; then
  if FRESH=$(gh auth token 2>/dev/null) && [ -n "$FRESH" ]; then
    mkdir -p "$(dirname "$TOKEN_FILE")" && chmod 700 "$(dirname "$TOKEN_FILE")"
    printf '%s' "$FRESH" > "$TOKEN_FILE" && chmod 600 "$TOKEN_FILE"
  fi
fi

echo "-> Pushing to GitHub..." >> "$LOG_FILE"
git add drafts/ docs/ >> "$LOG_FILE" 2>&1
git commit -m "Auto-generate content for $(date +%Y-%m-%d)" >> "$LOG_FILE" 2>&1 || true # ignore error if nothing to commit

PUSH_OK=""
if [ -s "$TOKEN_FILE" ]; then
  TOKEN=$(cat "$TOKEN_FILE")
  # Redact the token from any output that lands in the log.
  if git push "${PUSH_URL/TOKEN/$TOKEN}" main 2>&1 | sed "s|$TOKEN|***TOKEN***|g" >> "$LOG_FILE"; then
    PUSH_OK=1
  fi
fi
# Fallback to the gh credential helper (works when run interactively).
if [ -z "$PUSH_OK" ]; then
  if git -c credential.helper='!gh auth git-credential' push origin main >> "$LOG_FILE" 2>&1; then
    PUSH_OK=1
  fi
fi

if [ -n "$PUSH_OK" ]; then
  echo "   PUSH: ok" >> "$LOG_FILE"
else
  # Do NOT swallow this. A silent push failure means the live feed is stale
  # while drafts/ keeps advancing locally. Make it loud so cron.log + the QA
  # watchdog surface it.
  echo "   PUSH: FAILED <-- live site is now STALE, commits stuck local. Check gh auth + $TOKEN_FILE." >> "$LOG_FILE"
fi

echo "Done: $(date)" >> "$LOG_FILE"
