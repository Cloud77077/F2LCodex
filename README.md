# F2LCodex

F2LCodex is a beginner-friendly Telegram file-to-link bot. Users send a file to your Telegram bot; the app downloads it, stores it locally or in S3-compatible object storage, and replies with secure download and stream-page links served by FastAPI.

## Features

- FastAPI download, stream, health, webhook, and simple admin API routes.
- aiogram 3.x bot commands: `/start`, `/help`, and `/limits`.
- SQLAlchemy 2.x async models using SQLite by default.
- Local storage by default; optional S3-compatible storage.
- Cryptographically random URL-safe tokens stored only as HMAC hashes.
- HTTP Range request support for media seeking and resumable downloads.
- Optional `X-Accel-Redirect` support for protected Nginx file serving.
- Docker Compose stack with app, Nginx, and optional Telegram Bot API local server profile.
- Heroku Docker deployment files.

## Important defaults

- `MAX_FILE_SIZE_BYTES=0` means **no app-defined file-size limit**. Telegram and your infrastructure may still impose limits.
- `DEFAULT_LINK_TTL_HOURS=0` means links are **permanent** unless you change the value.
- Large-file Telegram support requires a **self-hosted Telegram Bot API server running in local mode**. The public Telegram Bot API has lower file limits; local mode is required when you want bot downloads/uploads beyond those hosted API limits.

## Quick start on your computer

1. Install Python 3.11+.
2. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and set:

   ```env
   BOT_TOKEN=your-token-from-botfather
   PUBLIC_BASE_URL=http://localhost:8000
   SECRET_KEY=a-long-random-secret
   ```

4. Install and run:

   ```bash
   pip install -e '.[test]'
   uvicorn app.main:app --reload
   ```

5. Configure a Telegram webhook after exposing the app over HTTPS:

   ```bash
   curl "https://api.telegram.org/bot$BOT_TOKEN/setWebhook?url=$PUBLIC_BASE_URL/telegram/webhook"
   ```

## Step-by-step VPS deployment with Docker Compose

This section assumes a fresh Ubuntu VPS, a domain such as `files.example.com`, and a Telegram bot token from [@BotFather](https://t.me/BotFather). Replace every example domain, path, and token with your real values.

### 1. Point your domain at the VPS

Create a DNS `A` record before installing TLS:

```text
files.example.com  A  YOUR_VPS_IPV4_ADDRESS
```

Wait until DNS resolves to the VPS:

```bash
dig +short files.example.com
```

### 2. Log in and install server packages

```bash
ssh root@YOUR_VPS_IPV4_ADDRESS
apt update && apt upgrade -y
apt install -y ca-certificates curl git ufw nginx certbot python3-certbot-nginx openssl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" > /etc/apt/sources.list.d/docker.list
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 3. Configure the firewall

Allow SSH, HTTP, and HTTPS. Keep app containers behind the reverse proxy in production.

```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable
ufw status
```

### 4. Download the project

Use your real repository URL if you deploy from a fork or private repo.

```bash
mkdir -p /opt/f2lcodex
cd /opt/f2lcodex
git clone YOUR_REPOSITORY_URL .
```

### 5. Create the production `.env` file

```bash
cp .env.example .env
SECRET=$(openssl rand -hex 32)
nano .env
```

A minimal local-storage VPS configuration looks like this:

```env
BOT_TOKEN=123456:replace-with-your-botfather-token
PUBLIC_BASE_URL=https://files.example.com
SECRET_KEY=paste-the-openssl-secret-here
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=./data/files
MAX_FILE_SIZE_BYTES=0
DEFAULT_LINK_TTL_HOURS=0
USE_X_ACCEL_REDIRECT=true
X_ACCEL_PREFIX=/protected/
ADMIN_TOKEN=another-long-random-string-if-you-use-the-api
```

Important meanings:

- `MAX_FILE_SIZE_BYTES=0` means the app itself does not enforce a file-size limit.
- `DEFAULT_LINK_TTL_HOURS=0` means generated links do not expire automatically.
- `USE_X_ACCEL_REDIRECT=true` lets the Nginx container serve stored files efficiently after FastAPI authorizes the token.

### 6. Start the containers

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f app
```

The compose stack starts:

- `app` on container port `8000`, published as VPS port `8000`.
- `nginx` on container port `80`, published as VPS port `8080`. This is the protected-file-serving Nginx used by `X-Accel-Redirect`.

### 7. Put public HTTPS Nginx in front

Create a host-level Nginx site that terminates TLS and proxies public traffic to the compose Nginx service on `127.0.0.1:8080`:

```bash
cat >/etc/nginx/sites-available/f2lcodex <<'EOF'
server {
    listen 80;
    server_name files.example.com;

    client_max_body_size 0;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }
}
EOF
ln -sf /etc/nginx/sites-available/f2lcodex /etc/nginx/sites-enabled/f2lcodex
nginx -t
systemctl reload nginx
certbot --nginx -d files.example.com
```

After Certbot finishes, test the app from your computer:

```bash
curl -i https://files.example.com/healthz
```

You should see a `200` response containing `{"ok":true}`.

### 8. Register the Telegram webhook

Run this on the VPS after `.env` contains the real `BOT_TOKEN` and `PUBLIC_BASE_URL`:

```bash
set -a
. ./.env
set +a
curl -sS "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=${PUBLIC_BASE_URL}/telegram/webhook"
curl -sS "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo"
```

Open your bot in Telegram, send `/start`, then send a small document. The bot should reply with `/d/...` and `/s/...` links.

### 9. Operate and update the service

Useful production commands:

```bash
cd /opt/f2lcodex
docker compose logs -f app
docker compose restart app
docker compose pull
git pull
docker compose up -d --build
scripts/backup.sh
```

### 10. Troubleshooting checklist

- `curl https://files.example.com/healthz` must return `200`.
- `docker compose ps` must show the app and Nginx containers running.
- `docker compose logs app` shows Python/FastAPI/bot errors.
- `docker compose logs nginx` shows protected-file-serving errors.
- `curl https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo` must show your HTTPS webhook URL and no recent delivery errors.
- If downloads are 404, confirm the bot generated the link after the current `SECRET_KEY` was set; changing `SECRET_KEY` invalidates old tokens.
- If large Telegram files fail, read the next section: you need a self-hosted Telegram Bot API server in local mode, not only `MAX_FILE_SIZE_BYTES=0`.

## Large Telegram files: local Bot API mode

For large files, run Telegram's Bot API server yourself in local mode and point the app at it:

```env
BOT_API_BASE_URL=http://telegram-bot-api:8081
MAX_FILE_SIZE_BYTES=0
```

Then start the optional compose profile:

```bash
docker compose --profile telegram-local up -d --build
```

You must provide `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` in `.env`. Get them from Telegram's API development tools. Without local Bot API mode, large-file support is limited by Telegram's hosted Bot API limits even though this app's own default limit is disabled.

## Heroku deployment

1. Create a Heroku app with container stack.
2. Configure environment variables from `.env.example` in Heroku config vars.
3. Deploy with the included `heroku.yml` or `Procfile`.
4. Use S3-compatible storage for durable file storage on Heroku, because Heroku dyno filesystems are ephemeral.

## S3-compatible storage

Set:

```env
STORAGE_BACKEND=s3
S3_ENDPOINT_URL=https://your-provider.example
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...
S3_BUCKET=f2lcodex
S3_REGION=us-east-1
```

## Backups and restores

Local deployments can back up `data/` and `.env`:

```bash
scripts/backup.sh
scripts/restore.sh backups/your-backup.tar.gz
```

For S3 deployments, back up the database and your bucket according to your provider's tools.

## Development

Run tests:

```bash
pip install -e '.[test]'
pytest
```

## Security notes

- Keep `SECRET_KEY` private. Changing it invalidates existing links because token hashes are HMAC-based.
- Use HTTPS in production.
- Set `ADMIN_TOKEN` if exposing `/api/files` publicly.
- Links are bearer secrets; anyone with a link can access the file until it expires or is revoked in the database.

## Project structure

- `app/main.py` creates the FastAPI app and Telegram webhook.
- `app/bot.py` defines aiogram handlers.
- `app/file_store.py` creates secure records and stores files.
- `app/storage/` contains local and S3 storage backends.
- `app/routes/` contains download, stream, API, and health routes.
- `app/utils/` contains MIME, token, Range, and human formatting helpers.
