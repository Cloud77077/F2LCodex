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

## Docker Compose VPS deployment

1. Install Docker and Docker Compose on the VPS.
2. Clone this repository and create `.env` from `.env.example`.
3. Set `PUBLIC_BASE_URL` to your HTTPS domain and set a strong `SECRET_KEY`.
4. Start the app:

   ```bash
   docker compose up -d --build
   ```

5. If you want Nginx to serve local files efficiently, set:

   ```env
   USE_X_ACCEL_REDIRECT=true
   X_ACCEL_PREFIX=/protected/
   ```

   The bundled `nginx/nginx.conf` marks `/protected/` as `internal`, so users cannot bypass the app and fetch arbitrary files directly.

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
