#!/usr/bin/env sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$script_dir"

[ -f client.env ] || {
  echo "missing client.env; run ./generate-config.sh first" >&2
  exit 1
}

# shellcheck disable=SC1091
. ./client.env

command -v curl >/dev/null 2>&1 || {
  echo "curl is required" >&2
  exit 1
}
command -v ffprobe >/dev/null 2>&1 || {
  echo "ffprobe is required" >&2
  exit 1
}
command -v jq >/dev/null 2>&1 || {
  echo "jq is required" >&2
  exit 1
}

tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT HUP INT TERM

verify_reel() {
  label=$1
  source_url=$2
  require_audio=$3
  response_file="$tmp_dir/$label-response.json"
  media_file="$tmp_dir/$label.mp4"

  curl --fail --silent --show-error \
    --request POST "$COBALT_API_URL" \
    --header "Accept: application/json" \
    --header "Content-Type: application/json" \
    --header "Authorization: Api-Key $COBALT_API_KEY" \
    --data "$(jq -cn --arg url "$source_url" '{url:$url,downloadMode:"auto",videoQuality:"max",localProcessing:"disabled"}')" \
    --output "$response_file"

  status=$(jq -r '.status // empty' "$response_file")
  case "$status" in
    tunnel|redirect)
      delivery_url=$(jq -r '.url // empty' "$response_file")
      ;;
    picker)
      delivery_url=$(jq -r '[.picker[] | select(.type == "video")][0].url // empty' "$response_file")
      ;;
    *)
      error_code=$(jq -r '.error.code // "unknown"' "$response_file")
      echo "$label failed: status=$status code=$error_code" >&2
      return 1
      ;;
  esac

  [ -n "$delivery_url" ] || {
    echo "$label failed: no video delivery URL" >&2
    return 1
  }

  curl --fail --location --silent --show-error \
    --max-time 300 \
    --header "Authorization: Api-Key $COBALT_API_KEY" \
    "$delivery_url" \
    --output "$media_file"

  has_video=$(ffprobe -v error -show_entries stream=codec_type -of json "$media_file" | jq 'any(.streams[]; .codec_type == "video")')
  has_audio=$(ffprobe -v error -show_entries stream=codec_type -of json "$media_file" | jq 'any(.streams[]; .codec_type == "audio")')
  size=$(wc -c < "$media_file" | tr -d ' ')

  [ "$has_video" = "true" ] || {
    echo "$label failed: downloaded file has no video stream" >&2
    return 1
  }
  if [ "$require_audio" = "true" ] && [ "$has_audio" != "true" ]; then
    echo "$label failed: downloaded file has no audio stream" >&2
    return 1
  fi

  echo "$label ok: status=$status bytes=$size video=$has_video audio=$has_audio"
}

verify_reel \
  "DZsVvmmkqXA" \
  "https://www.instagram.com/reel/DZsVvmmkqXA/" \
  "true"

verify_reel \
  "DZwITAaBfBE" \
  "https://www.instagram.com/reel/DZwITAaBfBE/" \
  "false"
