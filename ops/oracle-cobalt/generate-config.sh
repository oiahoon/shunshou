#!/usr/bin/env sh
set -eu

usage() {
  echo "usage: $0 cobalt.example.com" >&2
  exit 2
}

[ "$#" -eq 1 ] || usage

host=$1
case "$host" in
  *[!A-Za-z0-9.-]*|.*|*.)
    echo "invalid hostname: $host" >&2
    exit 2
    ;;
esac

command -v openssl >/dev/null 2>&1 || {
  echo "openssl is required" >&2
  exit 1
}

hex=$(openssl rand -hex 16)
api_key=$(printf '%s' "$hex" | sed -E 's/^(.{8})(.{4}).(.{3}).(.{3})(.{12})$/\1-\2-4\3-8\4-\5/')

umask 077
printf 'COBALT_HOST=%s\n' "$host" > .env
printf 'COBALT_API_URL=https://%s/\nCOBALT_API_KEY=%s\n' "$host" "$api_key" > client.env
printf '{\n  "%s": {\n    "name": "insta-share",\n    "limit": 10,\n    "allowedServices": ["instagram"]\n  }\n}\n' "$api_key" > keys.json

echo "Created .env, client.env, and keys.json with mode 0600."
echo "Keep client.env and keys.json private."
