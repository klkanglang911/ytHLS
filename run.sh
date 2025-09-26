#!/usr/bin/env bash
set -euo pipefail

cd /www/wwwroot/ythls-FastAPI

# 环境变量覆盖 AYAR.yml 中的 SECURITY 配置
export YTHLS_REQUIRE_API_KEY=true
export YTHLS_API_KEYS="Sunkey9827,Sunkey0711"

exec /www/wwwroot/ythls-FastAPI/venv/bin/python basla.py
