#!/usr/bin/env bash
set -euo pipefail

cd /www/wwwroot/ythls-FastAPI

# 环境变量覆盖 AYAR.yml 中的 SECURITY 配置
export YTHLS_REQUIRE_API_KEY=true
export YTHLS_API_KEYS="<api key1>,<api key2>"

exec /www/wwwroot/ythls-FastAPI/venv/bin/python basla.py
