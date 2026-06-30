# F2LCodex — Telegram File-to-Link and Stream Bot

F2LCodex is a Telegram bot plus FastAPI web app that turns Telegram files into secure download links and browser stream pages. A user sends a document, video, audio file, photo, archive, APK, ZIP, or another Telegram-supported file to the bot; the app stores the file and replies with links.

> **Important:** this project is designed with **no app-defined file-size limit by default**. That does not mean unlimited hosting. Real limits come from Telegram, the Telegram Bot API mode you use, disk space, bandwidth, memory, reverse proxy settings, object storage limits, and your deployment platform.

## Features

- Telegram bot powered by aiogram 3.x.
- FastAPI web routes for downloads, raw streams, stream pages, API metadata, and health checks.
- SQLite by default through SQLAlchemy 2.x async models.
- Optional S3-compatible object storage support.
- Secure random URL-safe tokens stored as HMAC hashes.
- HTTP Range request support for resumable downloads and media seeking.
- Python streaming fallback that does not load whole files into RAM.
- Optional Nginx `X-Accel-Redirect` support for faster protected local-file serving.
- Docker, Docker Compose, Nginx, Heroku, backup, and restore files included.
- pytest test suite for range parsing, token safety, filename sanitization, expiry, MIME helpers, and human-readable sizes.

## How it works

1. A Telegram user sends a file to the bot.
2. The bot reads Telegram metadata such as file ID, unique file ID, file name, MIME type, size, sender, chat, message ID, and caption.
3. The app downloads the file from Telegram using the configured Bot API endpoint.
4. The file is stored locally or in S3-compatible storage.
5. A database record is created with secure tokens and file metadata.
6. The bot replies with links for download and streaming.
7. A browser or download manager requests a link.
8. FastAPI validates the token and expiry status.
9. In local storage deployments, Nginx can serve the protected file through `X-Accel-Redirect`; otherwise the app streams the file in chunks.

## Telegram limits explained

Telegram itself controls what users can send to a bot. This app should not add another file-size limit unless you explicitly configure one.

- `MAX_FILE_SIZE_BYTES=0` means **no app-defined size limit**.
- If `MAX_FILE_SIZE_BYTES` is greater than zero, files larger than that value should be rejected.
- Files are still limited by Telegram, disk space, bandwidth, object storage rules, reverse proxy configuration, and deployment platform.
- Large files need enough server disk space because Telegram downloads and local storage can temporarily or permanently use many gigabytes.

## Public Bot API vs Local Bot API

The public Telegram Bot API is convenient, but it is not suitable for reliable large-file downloads. For production large-file support, run a self-hosted Telegram Bot API server in **local mode**.

In local mode:

- The Telegram Bot API server runs next to your app.
- It can download files without the same public Bot API file-download restriction.
- `getFile` can return local paths that the app can copy, hard-link, or move into storage.
- The app must validate paths, sanitize file names, and never expose raw server paths.

Recommended production values:

```env
BOT_API_BASE_URL=http://telegram-bot-api:8081
MAX_FILE_SIZE_BYTES=0
```

This repository currently uses `PUBLIC_BASE_URL` for generated links. If your deployment guide or hosting provider calls this value `BASE_URL`, use the same URL value for `PUBLIC_BASE_URL` in this app.

## What you need before starting

- A Telegram bot token from BotFather.
- A domain name for production, for example `files.example.com`.
- A VPS for best performance, or a Heroku app for a smaller/demo setup.
- Telegram API ID and API hash if you want local Bot API mode.
- Basic ability to copy and paste terminal commands.

## Which deployment should I choose?

Choose **VPS** if you want best speed and large-file support.

- Best for large files.
- Best for local Telegram Bot API mode.
- Best for Nginx high-speed downloads and streaming.
- You control disk space and bandwidth.

Choose **Heroku** only for demos or smaller setups unless using S3-compatible storage.

- Heroku filesystems are ephemeral, meaning local files can disappear after restarts or dyno replacement.
- Heroku is not ideal for running a local Telegram Bot API server and Nginx in the same way as a VPS.
- For Heroku, use `STORAGE_BACKEND=s3` with AWS S3, Cloudflare R2, Backblaze B2, or another S3-compatible provider.

## Environment variables explained

Copy `.env.example` to `.env` and edit it.

```bash
cp .env.example .env
nano .env
```

Current project variables:

| Variable | Meaning |
| --- | --- |
| `BOT_TOKEN` | Telegram bot token from BotFather. |
| `PUBLIC_BASE_URL` | Public URL used in generated links, for example `https://files.example.com`. |
| `SECRET_KEY` | Long random secret used to hash link tokens. Keep it private. |
| `DATABASE_URL` | SQLAlchemy database URL. SQLite is the default. |
| `STORAGE_BACKEND` | `local` or `s3`. |
| `LOCAL_STORAGE_PATH` | Local folder where files are stored. |
| `MAX_FILE_SIZE_BYTES` | `0` means no app-defined limit. |
| `DEFAULT_LINK_TTL_HOURS` | `0` means links do not expire automatically. |
| `USE_X_ACCEL_REDIRECT` | Set `true` to let Nginx serve protected local files. |
| `X_ACCEL_PREFIX` | Internal Nginx prefix used with `X-Accel-Redirect`. |
| `BOT_API_BASE_URL` | Optional custom Telegram Bot API URL, usually local Bot API server. |
| `ADMIN_TOKEN` | Optional token for protected admin API routes. |
| `S3_ENDPOINT_URL` | S3-compatible service endpoint. |
| `S3_ACCESS_KEY_ID` | S3 access key. |
| `S3_SECRET_ACCESS_KEY` | S3 secret key. |
| `S3_BUCKET` | Bucket name. |
| `S3_REGION` | S3 region. |

Requested production deployments may also use names such as `BASE_URL`, `STORAGE_DIR`, `ENABLE_NGINX_ACCEL`, `NGINX_ACCEL_PREFIX`, `AUTHORIZED_USER_IDS`, and `ADMIN_USER_IDS`. If you add those compatibility variables later, keep the meaning the same and avoid committing secrets.

## Bot commands

Implemented commands may depend on the current code version. The intended command set is:

- `/start` — explain what the bot does and how to send a file.
- `/help` — explain supported files, links, streaming, and limits.
- `/limits` — explain Telegram, server, and deployment limits.
- `/ping` — health check.
- `/myfiles` — show recent uploads for the current user.
- `/stats` — admin-only totals.
- `/delete <token>` — delete a file if you are the uploader or an admin.
- `/privacy` — explain stored data.

## Streaming support explained

The raw stream endpoint supports HTTP Range requests so browsers can seek in playable video and audio files. The stream page can show an HTML5 player for browser-supported media types such as MP4, WebM, Ogg video, MP3, M4A, Ogg audio, WAV, and WebM audio.

No transcoding is enabled by default. The app serves the original file.

## Why some videos do not play in browser

Browsers cannot play every video container or codec. MKV, AVI, HEVC/H.265, DTS audio, and some uncommon codecs may fail even when the file downloads correctly.

If a file does not play:

- Try downloading it and opening it in VLC.
- Try another browser.
- Convert the file to browser-friendly MP4 with H.264 video and AAC audio outside this app.

## Storage options: local and S3-compatible

### Local storage

Local storage is recommended for VPS deployments with Nginx acceleration.

Pros:

- Fast when the VPS disk and network are good.
- Works well with `X-Accel-Redirect`.
- Simple to back up with tar or rsync.

Cons:

- You must monitor disk usage.
- Files disappear if your server disk is deleted.

### S3-compatible storage

S3-compatible storage is recommended for Heroku and other ephemeral platforms.

Pros:

- Durable external file storage.
- Better fit for platforms where local disk is temporary.
- Can support signed URLs depending on configuration.

Cons:

- Usually costs extra.
- Streaming speed depends on object storage provider and region.
- Nginx local-file acceleration does not apply.

## Security settings

- Keep `SECRET_KEY` private.
- Use HTTPS in production.
- Use a private bot or user allowlist for sensitive deployments.
- Treat links as bearer secrets: anyone with the link can access the file.
- Sanitize file names and never expose raw server paths.
- Validate tokens and path traversal attempts.
- Add rate limiting before exposing a public bot.
- Do not run an open public piracy host.

## Admin-only mode

For stricter deployments, add or implement allowlist settings so only trusted Telegram user IDs can upload files. If a bot is open to everyone, strangers can abuse your server storage and bandwidth.

Recommended policy:

```env
AUTHORIZED_USER_IDS=123456789,987654321
ADMIN_USER_IDS=123456789
```

If these variables are not supported by the current code version, add them before running a public deployment.

## Deploy on a VPS — beginner friendly

These steps assume Ubuntu 22.04 or 24.04.

### 1. Buy a VPS

Recommended minimum:

- 2 CPU cores.
- 2 GB RAM minimum, 4 GB recommended.
- Enough disk space for stored Telegram files.
- Good bandwidth.

Large files need large disks. If users upload 100 GB of files, your server needs more than 100 GB of usable storage.

### 2. Point your domain to the VPS

In your domain DNS panel, create an A record:

- Type: `A`
- Name: `@` or a subdomain such as `files`
- Value: your VPS IP address

DNS can take minutes or hours to update.

### 3. Connect to the VPS with SSH

Windows PowerShell:

```powershell
ssh root@YOUR_SERVER_IP
```

macOS/Linux Terminal:

```bash
ssh root@YOUR_SERVER_IP
```

### 4. Install Docker and Docker Compose

```bash
apt update
apt install -y ca-certificates curl gnupg git nano
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" > /etc/apt/sources.list.d/docker.list
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Verify:

```bash
docker --version
docker compose version
```

### 5. Clone your GitHub repository

```bash
git clone <your-repo-url>
cd F2LCodex
```

If Codex pushed these files to your repository, clone that same repository.

### 6. Create `.env`

```bash
cp .env.example .env
nano .env
```

Set these important values:

- `BOT_TOKEN`: from BotFather.
- `PUBLIC_BASE_URL`: your public URL, for example `https://files.example.com`.
- `SECRET_KEY`: a long random string.
- `BOT_API_BASE_URL`: `http://telegram-bot-api:8081` if using local Bot API mode.
- `MAX_FILE_SIZE_BYTES`: keep `0` for no app-defined limit.

### 7. Get Telegram credentials

- Bot token: message `@BotFather` on Telegram and create a bot.
- API ID and API hash: create an application at Telegram's developer portal.

The bot token and API ID/hash are not the same thing. The bot token identifies your bot. API ID/hash are needed to run Telegram's local Bot API server.

### 8. Start the bot

```bash
docker compose up -d --build
```

View logs:

```bash
docker compose logs -f app
docker compose logs -f telegram-bot-api
```

### 9. Test it

1. Open Telegram.
2. Send `/start` to the bot.
3. Send a small video.
4. Open the download link.
5. Open the stream page.
6. Try seeking in the video player.

### 10. Enable HTTPS

#### Easy option: Caddy in front of this stack

Install Caddy and point it to the Nginx service or host port you expose:

```bash
apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' > /etc/apt/sources.list.d/caddy-stable.list
apt update
apt install -y caddy
```

Example Caddyfile:

```caddyfile
files.example.com {
    reverse_proxy 127.0.0.1:8080
}
```

Then restart Caddy:

```bash
systemctl reload caddy
```

#### Nginx + Certbot option

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d files.example.com
```

After HTTPS works, make sure `PUBLIC_BASE_URL=https://files.example.com`.

### 11. Updating the bot

```bash
git pull
docker compose build
docker compose up -d
```

### 12. Backup

Back up:

- `.env`
- database file
- local file storage directory

Example:

```bash
tar -czf f2lcodex-backup-$(date +%F).tar.gz .env data
```

### 13. Common VPS problems and fixes

- **Domain not opening:** check DNS A record, firewall, and container ports.
- **Bot not replying:** check `BOT_TOKEN`, logs, and webhook configuration.
- **Large files failing:** use local Telegram Bot API mode and confirm disk space.
- **Video page opens but video does not play:** browser may not support the codec.
- **Download is slow:** speed depends on VPS network, disk, Telegram download speed, user network, reverse proxy config, and server region.
- **No disk space left:** delete old files or increase VPS disk size.
- **Permission denied:** check mounted volume ownership.
- **Docker container restarting:** run `docker compose logs -f app`.
- **Telegram API ID/hash wrong:** regenerate or recheck values in Telegram developer portal.
- **Public URL wrong:** fix `PUBLIC_BASE_URL` and restart containers.

## Deploy on Heroku — beginner friendly but not recommended for large local storage

Heroku warning:

- Heroku filesystem is ephemeral.
- Files saved to local disk can disappear when the dyno restarts.
- Heroku is not recommended for large permanent file hosting with local storage.
- Use `STORAGE_BACKEND=s3` with AWS S3, Cloudflare R2, Backblaze B2, or another compatible service.
- Heroku may not be ideal for running local Telegram Bot API server and Nginx in the same way as a VPS.
- VPS deployment is recommended for best large-file performance.

### Heroku steps

1. Create a Heroku account.
2. Install the Heroku CLI.
3. Log in:

   ```bash
   heroku login
   ```

4. Create an app:

   ```bash
   heroku create your-app-name
   ```

5. Add Heroku Postgres:

   ```bash
   heroku addons:create heroku-postgresql:essential-0
   ```

6. Set config vars:

   ```bash
   heroku config:set BOT_TOKEN=...
   heroku config:set PUBLIC_BASE_URL=https://your-app-name.herokuapp.com
   heroku config:set STORAGE_BACKEND=s3
   heroku config:set S3_ENDPOINT_URL=...
   heroku config:set S3_ACCESS_KEY_ID=...
   heroku config:set S3_SECRET_ACCESS_KEY=...
   heroku config:set S3_BUCKET=...
   heroku config:set S3_REGION=...
   heroku config:set SECRET_KEY=...
   ```

7. Deploy using Heroku Container Registry:

   ```bash
   heroku container:login
   heroku stack:set container
   heroku container:push web
   heroku container:release web
   ```

8. Open logs:

   ```bash
   heroku logs --tail
   ```

9. Test the bot from Telegram.

10. Remember Heroku limitations:
    - Ephemeral filesystem.
    - Dyno sleep or cost depending on plan.
    - Bandwidth and performance limits.
    - Large file streaming may be slower.
    - Not recommended without external object storage.

## Updating the bot

For VPS deployments:

```bash
git pull
docker compose build
docker compose up -d
```

For Heroku container deployments:

```bash
heroku container:push web
heroku container:release web
```

## Backup and restore

Use the included scripts for local deployments:

```bash
scripts/backup.sh
scripts/restore.sh backups/your-backup.tar.gz
```

Always verify backups before deleting files.

## Troubleshooting

### The bot does not answer

Check logs and the bot token:

```bash
docker compose logs -f app
```

### Download links point to the wrong domain

Set `PUBLIC_BASE_URL` to the exact public URL and restart the app.

### Large files fail

Use local Telegram Bot API mode, check disk space, and verify reverse proxy settings.

### Downloads do not resume

Confirm the route returns `Accept-Ranges`, `Content-Range`, and correct status codes for Range requests.

### Stream page works but seeking fails

Check Range request support and make sure your reverse proxy does not strip Range headers.

## FAQ

### Is this unlimited file hosting?

No. The app has no file-size limit by default, but Telegram and your server still have real limits.

### Can I run this publicly?

You can, but it is risky. Public bots can be abused for piracy, malware hosting, and bandwidth theft. Use allowlists and rate limits.

### Does it transcode videos?

No. It serves original files. Browser playback depends on browser codec support.

### Is S3 required?

No for VPS local storage. Yes or strongly recommended for Heroku and ephemeral platforms.

## Legal and abuse warning

Users are responsible for hosting and sharing only files they have rights to share. Do not use this project to host pirated, illegal, abusive, or harmful content. Operators should remove illegal content and restrict access when needed.

## Contributing

Contributions are welcome. Please keep changes simple, typed where practical, tested with pytest, and formatted with the configured Python tooling.

## License

This project is released under the MIT License. See `LICENSE` for details.

## Final checklist

Before production:

- [ ] Set `BOT_TOKEN`.
- [ ] Set `PUBLIC_BASE_URL` to HTTPS domain.
- [ ] Set a strong `SECRET_KEY`.
- [ ] Decide local storage or S3.
- [ ] Use local Telegram Bot API mode for large files.
- [ ] Enable HTTPS.
- [ ] Confirm downloads support resume.
- [ ] Confirm stream seeking works for MP4.
- [ ] Configure backups.
- [ ] Restrict bot access if the deployment is private.
