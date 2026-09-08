#!/usr/bin/env sh
set -eu

usage() {
  echo "usage: $0 PUBLIC_IP [SSH_USER]" >&2
  exit 2
}

[ "$#" -ge 1 ] && [ "$#" -le 2 ] || usage

public_ip=$1
ssh_user=${2:-ubuntu}
target="$ssh_user@$public_ip"

for file in .env keys.json Caddyfile docker-compose.yml; do
  [ -f "$file" ] || {
    echo "missing $file; run ./generate-config.sh first" >&2
    exit 1
  }
done

ssh "$target" "sudo install -d -m 0750 -o $ssh_user -g $ssh_user /opt/cobalt"
scp .env keys.json Caddyfile docker-compose.yml "$target:/opt/cobalt/"
ssh "$target" "chmod 600 /opt/cobalt/.env /opt/cobalt/keys.json && cd /opt/cobalt && docker compose pull && docker compose up -d"

echo "Deployment started. Check it with:"
echo "  ssh $target 'cd /opt/cobalt && docker compose ps'"
