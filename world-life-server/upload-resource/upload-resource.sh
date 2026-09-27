#!/usr/bin/env bash
set -euo pipefail

FILE="${1:?usage: upload-resource.sh FILE [REMOTE_NAME]}"
NAME="${2:-$(basename "$FILE")}"
: "${SUPABASE_URL:?set SUPABASE_URL}"
: "${SUPABASE_SERVICE_ROLE_KEY:?set SUPABASE_SERVICE_ROLE_KEY}"

case "$NAME" in
  *[!A-Za-z0-9_.-]*) echo "invalid resource name" >&2; exit 2 ;;
esac

SHA="$(sha256sum "$FILE" | awk '{print $1}')"
SIZE="$(stat -c '%s' "$FILE")"

echo "Uploading $NAME ($SIZE bytes), sha256=$SHA"

curl --fail-with-body --retry 3 \
  -X POST \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @"$FILE" \
  "$SUPABASE_URL/storage/v1/object/world-life-resources/resources/$NAME?upsert=true"

TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

curl --fail --retry 3 \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  "$SUPABASE_URL/storage/v1/object/world-life-resources/resources/$NAME" > "$TMP"

DOWN_SHA="$(sha256sum "$TMP" | awk '{print $1}')"
DOWN_SIZE="$(stat -c '%s' "$TMP")"

test "$SHA" = "$DOWN_SHA"
test "$SIZE" = "$DOWN_SIZE"

echo "VERIFIED: $NAME size=$DOWN_SIZE sha256=$DOWN_SHA"
