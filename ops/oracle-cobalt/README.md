# Oracle Always Free Cobalt

This package deploys a private Cobalt 11 API on an Oracle Ampere A1 VM. Cobalt
handles transient media tunneling and remuxing on the VM; no media is retained
after delivery.

## OCI instance

Create the instance in the tenancy home region and verify that every selected
resource is marked `Always Free-eligible`:

- Shape: `VM.Standard.A1.Flex`
- CPU and memory: use `1 OCPU / 6 GB` for this instance. This stays at half of
  the current `2 OCPU / 12 GB` A1 Always Free tenancy allowance.
- Image: Ubuntu 24.04 Minimal aarch64
- Boot volume: 50 GB
- Public IPv4: enabled
- SSH: add your public key; do not enable password login
- Cloud-init: paste `cloud-init.yaml` under advanced options

Before clicking Create, confirm the shape and boot volume are both marked
`Always Free-eligible` and that the estimated charge is zero. Stop if OCI shows
any non-zero recurring cost, paid image, paid support, or paid networking item.

Add ingress rules to the OCI subnet security list or network security group:

- TCP 22 from your current public IP only
- TCP 80 from `0.0.0.0/0`
- TCP 443 from `0.0.0.0/0`
- UDP 443 from `0.0.0.0/0` (optional HTTP/3)

Do not open port 9000. Cobalt is reachable only through Caddy.

## DNS and secrets

Create a DNS `A` record such as `cobalt.example.com` pointing to the VM public
IP. If the zone is on Cloudflare, start with DNS-only mode so large tunnel
responses do not pass through the Cloudflare proxy.

Generate a private API key locally:

```bash
cd ops/oracle-cobalt
chmod +x generate-config.sh deploy.sh verify-reels.sh
./generate-config.sh cobalt.example.com
```

The generated `.env`, `client.env`, and `keys.json` files are gitignored. The
API key is restricted to Instagram and ten resolve requests per minute.

## Deploy

Wait for cloud-init to finish, then deploy from this directory:

```bash
./deploy.sh VM_PUBLIC_IP
```

Check container and certificate status:

```bash
ssh ubuntu@VM_PUBLIC_IP 'cloud-init status --wait'
ssh ubuntu@VM_PUBLIC_IP 'cd /opt/cobalt && docker compose ps'
ssh ubuntu@VM_PUBLIC_IP 'cd /opt/cobalt && docker compose logs --tail=100'
```

## End-to-end verification

The verifier resolves both known Reel samples, downloads each transient result
to a temporary directory, checks the media streams with `ffprobe`, and deletes
the files on exit. The first sample must include both video and audio.

```bash
./verify-reels.sh
```

Rotate a leaked key by running `generate-config.sh` again and redeploying. Never
put `client.env` or `keys.json` into Vercel logs, issue comments, or Git.
