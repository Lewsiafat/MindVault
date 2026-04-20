# Deployment

MindVault ships two supported deployment styles. Pick one:

- **Docker Compose** — easiest; the recommended default.
- **Bare-metal** — uv + systemd + nginx; for users who want to skip Docker.

There is **no built-in authentication**. Put MindVault behind a reverse proxy (see below) and add whatever access control you need at that layer.

---

## Docker Compose

### Three-step install

```bash
git clone https://github.com/yourname/MindVault
cd MindVault
cp .env.example .env
# edit .env — at minimum set AI_PROVIDER and AI_API_KEY
docker compose up -d
```

The image is multi-stage:
1. `node:20-alpine` builds the Vue frontend → `src/static/`
2. `python:3.13-slim` installs deps with `uv sync --frozen --extra all` and runs uvicorn

### Volume mount

```
┌────────────────────────┐        ┌────────────────────────┐
│ Host                   │        │ Container              │
│                        │        │                        │
│ ${DATA_DIR:-./data}  ──┼───────▶│ /app/data              │
└────────────────────────┘        └────────────────────────┘
```

Whatever is at `DATA_DIR` on the host is what MindVault reads inside the container. Change `DATA_DIR` in `.env` and `docker compose up -d` again to switch notes folders.

### Port mapping

The container always listens on `10016` internally. `PORT` in `.env` controls the host port exposed by docker-compose:

```yaml
# docker-compose.yml
ports:
  - "${PORT:-10016}:10016"
```

For a VPS behind a reverse proxy, change to `"127.0.0.1:${PORT:-10016}:10016"` so the container isn't directly reachable from the internet.

### Updating

```bash
git pull
docker compose up -d --build
```

### Debugging

```bash
docker compose logs -f              # tail logs
docker compose exec mindvault sh    # shell into container
curl http://localhost:10016/mind-vault/api/health   # health check
```

### Gotchas

- **Ollama on the host:** use `http://host.docker.internal:11434/v1` (macOS/Windows) or `network_mode: host` (Linux).
- **Changing `BASE_PATH`:** you must also edit `frontend/vite.config.ts`'s `base` value and rebuild the image (`--build`).

---

## Bare-metal

Requires [uv](https://docs.astral.sh/uv/) and Node.js 20+.

### Install

```bash
git clone https://github.com/yourname/MindVault /srv/mindvault
cd /srv/mindvault

uv sync --extra all

cd frontend && npm install && npm run build && cd ..

cp .env.example .env
# fill AI_API_KEY, DATA_DIR, BASE_PATH as needed
```

### systemd unit

Save as `/etc/systemd/system/mindvault.service`:

```ini
[Unit]
Description=MindVault
After=network.target

[Service]
Type=simple
User=mindvault
WorkingDirectory=/srv/mindvault
EnvironmentFile=/srv/mindvault/.env
ExecStart=/srv/mindvault/.venv/bin/uvicorn src.main:app --host 127.0.0.1 --port 10016
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mindvault
sudo journalctl -u mindvault -f
```

---

## Reverse proxy

### nginx

```nginx
location /mind-vault/ {
    proxy_pass http://127.0.0.1:10016/mind-vault/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

Add basic auth if you want a simple access gate:

```nginx
location /mind-vault/ {
    auth_basic "MindVault";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://127.0.0.1:10016/mind-vault/;
    # ... other proxy headers as above
}
```

### Caddy

```caddy
your.domain {
    reverse_proxy /mind-vault/* 127.0.0.1:10016
}
```

### Cloudflare Access / Tailscale / VPN

All work. None require any config on the MindVault side — just don't expose port 10016 to the public internet.

---

## Backups

Back up `DATA_DIR`. That's it — the app itself is stateless, the only durable state is your markdown files (and the regenerable wiki/cache inside them). Restic, borg, rsync, or the git-repo mode from [`data-management.md`](./data-management.md) all work.
