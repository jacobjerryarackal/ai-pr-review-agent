#!/bin/bash
# tools/send_test_webhook.sh
set -e

FIXTURE="${1:-tests/fixtures/pr_opened.json}"
URL="${URL:-http://localhost:8000/webhook/github}"
SECRET="${GITHUB_WEBHOOK_SECRET:-$(grep '^GITHUB_WEBHOOK_SECRET=' .env | cut -d= -f2)}"

if [ ! -f "$FIXTURE" ]; then
  echo "fixture not found: $FIXTURE" >&2
  exit 2
fi

BODY=$(cat "$FIXTURE")
SIG=$(python3 tools/sign.py "$BODY" "$SECRET")
DID="local-$(date +%s%N)"

echo ">>> POST $URL"
echo "    X-GitHub-Event: pull_request"
echo "    X-GitHub-Delivery: $DID"
echo "    X-Hub-Signature-256: $SIG"
echo "    body: $(echo "$BODY" | wc -c) bytes from $FIXTURE"
echo

curl -i -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -H "X-GitHub-Delivery: $DID" \
  -H "X-Hub-Signature-256: $SIG" \
  --data-binary "$BODY"
echo