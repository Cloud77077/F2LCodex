#!/usr/bin/env bash
set -euo pipefail
mkdir -p backups
tar -czf "backups/f2lcodex-$(date +%Y%m%d-%H%M%S).tar.gz" data .env 2>/dev/null || tar -czf "backups/f2lcodex-$(date +%Y%m%d-%H%M%S).tar.gz" data
