#!/bin/bash
# VPS deployment script for SplitSmart India
# Usage:
#   1. Edit .env (copy from .env.production.example)
#   2. Edit nginx/conf.d/app.conf (copy from .conf.template, replace YOUR_DOMAIN)
#   3. Run: bash deploy-vps.sh

set -e

if [ ! -f .env ]; then
    echo "ERROR: .env not found. Copy .env.production.example to .env and edit it."
    exit 1
fi

if [ ! -f nginx/conf.d/app.conf ]; then
    echo "ERROR: nginx/conf.d/app.conf not found."
    echo "  - For domain + SSL: cp nginx/conf.d/app.conf.template nginx/conf.d/app.conf"
    echo "  - For IP only:      cp nginx/conf.d/app-http-only.conf.template nginx/conf.d/app.conf"
    echo "  Then edit it (replace YOUR_DOMAIN if applicable)."
    exit 1
fi

echo "==> Pulling latest code..."
git pull

echo "==> Building containers..."
docker compose -f docker-compose.prod.yml build

echo "==> Starting services..."
docker compose -f docker-compose.prod.yml up -d

echo "==> Waiting for backend to be ready..."
sleep 10

echo "==> Checking status..."
docker compose -f docker-compose.prod.yml ps

echo ""
echo "Deployment complete."
echo "Logs: docker compose -f docker-compose.prod.yml logs -f"
echo "Shell: docker compose -f docker-compose.prod.yml exec backend bash"
