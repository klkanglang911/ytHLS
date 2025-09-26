# ythls-FastAPI

[![Size](https://img.shields.io/github/repo-size/keyiflerolsun/ythls-FastAPI?logo=git&logoColor=white&label=Size)](#)
[![Views](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/keyiflerolsun/ythls-FastAPI&title=Views)](#)
[![Version](https://img.shields.io/badge/Version-v1.1-blue)](#)
<a href="https://KekikAkademi.org/Kahve" target="_blank"><img src="https://img.shields.io/badge/☕️-Buy Me a Coffe-ffdd00" title="☕️ Buy Me a Coffe" style="padding-left:5px;"></a>

*Creates a permanent link for the live feed (HLS/m3u8) of a Youtube channel or video*

[![ForTheBadge made-with-python](https://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![ForTheBadge built-with-love](https://ForTheBadge.com/images/badges/built-with-love.svg)](https://GitHub.com/keyiflerolsun/)

## 📄 Description

**ythls-FastAPI** is a FastAPI application that retrieves HLS URLs and JSON data for YouTube videos and channels. The application provides data in both HLS and JSON formats using specific YouTube video and channel IDs.

## 📋 Features

- Retrieve HLS URLs for YouTube videos.
- Retrieve live stream HLS URLs for YouTube channels.
- Retrieve JSON data for YouTube videos.
- Retrieve live stream JSON data for YouTube channels.
- Log requests and store IP details.
- Fast and secure data retrieval.

## 📖 API Endpoints

| Method | Endpoint                                                      | Description                                                                                |
|--------|---------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| `GET`  | **https://ythls.kekikakademi.org/youtube**                    | _Provides information about the API and lists available endpoints._                        |
| `GET`  | **https://ythls.kekikakademi.org/youtube/channel/{id}.m3u8**  | _Get the HLS URL for a YouTube channel live stream. Replace `{id}` with the channel ID._   |
| `GET`  | **https://ythls.kekikakademi.org/youtube/video/{id}.m3u8**    | _Get the HLS URL for a YouTube video. Replace `{id}` with the video ID._                   |
| `GET`  | **https://ythls.kekikakademi.org/youtube/channel/{id}.json**  | _Get the JSON data for a YouTube channel live stream. Replace `{id}` with the channel ID._ |
| `GET`  | **https://ythls.kekikakademi.org/youtube/video/{id}.json**    | _Get the JSON data for a YouTube video. Replace `{id}` with the video ID._                 |

## 🌐 License and Copyright

* *Copyright (C) 2024 by* [keyiflerolsun](https://github.com/keyiflerolsun) ❤️️
* *Licensed under the* [GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007](https://github.com/keyiflerolsun/ythls-FastAPI/blob/master/LICENSE).

## ♻️ Contact

*Feel free to contact me on* **Telegram:** [@keyiflerolsun](https://t.me/KekikKahve)

## 💸 Donate

**[☕️ Buy Me a Coffe](https://KekikAkademi.org/Kahve)**

***

> *Written for* **[@KekikAkademi](https://t.me/KekikAkademi)**

---

# 🇨🇳 中文说明与部署指南

本项目已扩展“服务端 HLS 代理 + 清单改写”，可在中国大陆网络环境下，通过部署在海外 VPS 的本服务，直接在 VLC 等播放器收看 YouTube 直播/视频流，而无需客户端再直连 `googlevideo.com`。

## 功能综述

- YouTube 视频与频道数据获取（JSON 与 HLS）
- 两种后端解析模式：
  - `yt-dlp`（支持 `cookies.txt` 登录态，建议遇到受限内容时开启）
  - 网页解析（httpx + parsel）
- 中间件：请求日志、IP 归属查询（使用 `ip-api.com`）
- 全局缓存（TTL 由配置设定）
- 新增 HLS 全链路代理：改写 m3u8 清单并代理分片，客户端只访问你的域名即可播放

## 目录与关键文件

- 启动入口：`basla.py`（调用 `Core/Motor.py` 用 uvicorn 启动）
- 应用装配：`Core/__init__.py`（注册路由、静态资源、异常处理）
- 中间件与工具：`Core/Modules/_istek.py`（日志与超时）、`Core/Modules/_IP_Log.py`（IP 归属）
- 配置加载：`Settings/__init__.py` 读取 `AYAR.yml`
- YouTube 模块：`Public/YouTube/Libs/`（`YouTube.py`/`ytdl.py`）
- 路由：
  - YouTube：`Public/YouTube/Routers/`（`__init__.py`、`channel.py`、`video.py`、`proxy.py`）
  - 首页：`Public/Home/Routers/` 与模板/静态资源

## 配置说明（`AYAR.yml`）

```yaml
PROJE : ythls-FastAPI
APP   :
  HOST    : 127.0.0.1   # 推荐生产保持 127.0.0.1，仅供本机反代
  PORT    : 3310
  WORKERS : 1           # 可按 CPU 核心数调整
  CACHE   : 15          # 分钟

yt-dlp : true           # true=使用 yt-dlp 后端；false=使用网页解析

# 可选：API Key 访问控制
SECURITY:
  REQUIRE_API_KEY: false       # 设为 true 后，m3u8 与 proxy 路由将强制校验 API Key
  API_KEYS:
    - change-me-please         # 在此维护允许的 Key，可多个

也支持用“环境变量”覆盖（推荐生产使用）：

- `YTHLS_REQUIRE_API_KEY`: `true`/`false`
- `YTHLS_API_KEYS`: 逗号分隔的 Key 列表，如 `KeyA,KeyB`

示例（BT Supervisor 启动命令可直接前缀 env 变量）：

```
YTHLS_REQUIRE_API_KEY=true \
YTHLS_API_KEYS="Sunkey9827,Sunkey0711" \
/www/wwwroot/ythls-FastAPI/venv/bin/python basla.py
```

Docker 用户可通过 `-e` 传入：

```
docker run -e YTHLS_REQUIRE_API_KEY=true -e YTHLS_API_KEYS="KeyA,KeyB" ...
```
```

- 修改后重启应用生效；如启用 `yt-dlp` 并需登录，放置 `cookies.txt` 于项目根目录。

## API 端点（当前实现）

- `GET /youtube`：返回服务信息与可用端点列表
- `GET /youtube/channel/{id}.json`：获取频道直播 JSON
- `GET /youtube/video/{id}.json`：获取视频 JSON
- `GET /youtube/channel/{id}.m3u8`：返回“已改写”的 m3u8（后续清单/分片均经本服务代理）
- `GET /youtube/video/{id}.m3u8`：返回“已改写”的 m3u8
- 如开启 API Key：
  - 请求 m3u8/proxy 路由必须带 Key（两种方式任一即可）：
    - 请求头：`X-API-Key: <your-key>`
    - 查询参数：`?k=<your-key>`（系统会将该参数自动附加到清单中的所有代理 URL）
- `GET /youtube/channel/{id}/lives.json`：列出该频道当前所有“正在直播”的视频（包含 `id`/`title` 等）
- 频道多直播选择（在 m3u8 上使用查询参数）：
  - 按序号选（1 开始）：`/youtube/channel/{id}.m3u8?i=2`
  - 按标题包含关键字：`/youtube/channel/{id}.m3u8?q=关键字`
  - 显式指定 videoId：`/youtube/channel/{id}.m3u8?vid=VIDEO_ID`
- 代理端点（仅允许 YouTube 相关域名）：
  - `GET /youtube/proxy/m3u8?url=...`：拉取并改写上游 m3u8
  - `GET /youtube/proxy/seg?url=...`：代理分片，透传 Range/If-Range 等头

说明：`/youtube/channel|video/{id}.m3u8` 内部会使用上述代理端点改写清单，客户端不会直连上游域名。

## 本地运行

```bash
python -m pip install -r requirements.txt
python basla.py
# 打开 http://127.0.0.1:3310/youtube 验证
```

## 部署（Debian + 宝塔面板，推荐方案：Python venv + Supervisor + Nginx 反代）

1) 上传代码至服务器
- 路径建议：`/www/wwwroot/ythls-FastAPI`
- 赋权（SSH）：`chown -R www:www /www/wwwroot/ythls-FastAPI`

2) 安装依赖与虚拟环境（SSH/终端）
```bash
apt-get update -y && apt-get install -y python3-venv python3-pip
cd /www/wwwroot/ythls-FastAPI
python3 -m venv venv && source venv/bin/activate
pip install -U pip setuptools wheel
pip install -r requirements.txt
```

3) 前台验证
```bash
source venv/bin/activate
python basla.py
# 新开终端：curl http://127.0.0.1:3310/youtube
```

4) 用宝塔 Supervisor 托管
- 新建进程：运行目录 `/www/wwwroot/ythls-FastAPI`
- 启动命令：`/www/wwwroot/ythls-FastAPI/venv/bin/python basla.py`
- 自动启动/重启：开启

5) Nginx 反向代理（单站点完整示例）

将站点配置为下列内容（面板“配置文件”中替换），已包含根路径反代与 HLS 优化。

```
server
{
    listen 80;
    server_name ht.982788.xyz;  # 改为你的域名
    index index.php index.html index.htm default.php default.htm default.html;
    root /www/wwwroot/ythls-FastAPI;

    # 证书申请校验
    include /www/server/panel/vhost/nginx/well-known/ht.982788.xyz.conf;

    # 错误页
    error_page 404 /404.html;

    # 根路径反代
    location / {
        proxy_pass http://127.0.0.1:3310;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
    }

    # HLS 优化：禁用缓冲 + 透传 Range
    location ~* \.(m3u8|ts|m4s)$ {
        proxy_pass http://127.0.0.1:3310;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Range $http_range;
        proxy_set_header If-Range $http_if_range;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
    }

    # PHP（如无需可保留或移除）
    include enable-php-00.conf;

    # 伪静态
    include /www/server/panel/vhost/rewrite/ht.982788.xyz.conf;

    # 访问限制
    location ~ ^/(\.user\.ini|\.htaccess|\.git|\.env|\.svn|\.project|LICENSE|README\.md) {
        return 404;
    }

    # 证书验证目录
    location ~ \.well-known { allow all; }
    if ($uri ~ "^/\.well-known/.*\.(php|jsp|py|js|css|lua|ts|go|zip|tar\.gz|rar|7z|sql|bak)$") { return 403; }

    access_log  /www/wwwlogs/ht.982788.xyz.log;
    error_log   /www/wwwlogs/ht.982788.xyz.error.log;
}
```

6) HTTPS
- 面板 → 站点 → SSL → Let’s Encrypt 申请并开启“强制 HTTPS”。

## Docker Compose（可选）

```bash
# 修改 AYAR.yml 中 HOST 为 0.0.0.0（容器内监听对外）
docker compose up -d --build
# 端口映射见 docker-compose.yml（默认 1453:3310）
```
- 若用 Nginx 反代容器，请将 `proxy_pass` 指向 `http://127.0.0.1:1453`。

## 常见问题（FAQ）

- 端口被占用（Supervisor 启动即退出）
  - `ss -lptn | grep :3310` 找到 PID，`kill <PID>` 释放；或改 `AYAR.yml` 的 `PORT` 并更新反代。
- 502/网关错误
  - 检查后端是否运行、反代目标是否正确（`127.0.0.1:3310`）。
- 播放失败或卡顿
  - 确保使用的是本服务导出的 m3u8（路径以 `/youtube/...m3u8`）；Nginx 对 `.m3u8/.ts/.m4s` 关闭缓冲；服务器带宽充足。
- API Key 提示 401/403
  - 401：缺少 Key；403：Key 不在白名单。按 `AYAR.yml` 的 `SECURITY.API_KEYS` 配置允许列表，并在请求中携带 `X-API-Key` 或 `?k=`。
- 返回 “Upstream host not allowed”
  - 代理白名单仅允许 YouTube 相关域名，可在 `Public/YouTube/Routers/proxy.py` 中扩展。
- `yt-dlp` 登录
  - 将 `cookies.txt` 放在项目根目录，避免提交到仓库；合法使用，注意合规与隐私。

## 版本

- v1.1
  - 新增：API Key 访问控制（`SECURITY.REQUIRE_API_KEY`/`SECURITY.API_KEYS`）
  - 新增：环境变量覆盖配置（`YTHLS_REQUIRE_API_KEY`、`YTHLS_API_KEYS`）
  - 文档：README 更新、Supervisor 启动示例（含 run.sh 包装脚本）
  - 优化：清单改写会自动附带 `k=` 参数到所有代理 URL，便于 VLC 使用查询参数传 Key

- v1.0
  - 新增：HLS 全链路代理与 m3u8 清单改写（客户端仅访问本站域名即可播放）
  - 新增：频道多直播选择（`/youtube/channel/{id}/lives.json` 与 `i`/`q`/`vid` 选择参数）
  - 文档：补充 Debian + 宝塔面板的部署步骤与 Nginx 示例
  - 优化：HLS 反代的缓冲与 Range 透传配置示例
- 说明：保留 `yt-dlp` 与网页解析两种模式，支持 `cookies.txt`

## 开源发布与配置模板

- 使用模板：仓库附带 `AYAR.example.yml`，部署前请复制为实际配置：
  - `cp AYAR.example.yml AYAR.yml`，再按需修改。
  - 切勿将真实 `AYAR.yml` 提交到仓库（`.gitignore` 已默认忽略）。
- 管理密钥：生产环境建议用环境变量覆盖，而非明文写入 `AYAR.yml`。
  - `YTHLS_REQUIRE_API_KEY=true|false`
  - `YTHLS_API_KEYS="KeyA,KeyB"`
  - Supervisor 启动示例：
    - `YTHLS_REQUIRE_API_KEY=true YTHLS_API_KEYS="Sunkey9827,Sunkey0711" /www/wwwroot/ythls-FastAPI/venv/bin/python basla.py`
  - 或包装脚本 `run.sh` 中设置上述环境变量。
- 忽略敏感文件：`.gitignore` 已包含 `AYAR.yml`、`cookies.txt`、虚拟环境、日志等。
  - 若误加到暂存区：`git rm --cached AYAR.yml cookies.txt -f && git commit -m "chore: drop secrets"`
  - 若已推送含密钥历史：请旋转密钥，并使用 `git filter-repo` 或 `git filter-branch` 清理历史。
- 推送到 GitHub（示例）：
  - `git init && git add . && git commit -m "v1.1"`
  - `git branch -M main && git remote add origin https://github.com/klkanglang911/YtFLS.git`
  - `git push -u origin main`

## Supervisor 启动脚本示例（run.sh）

- 建议用一个包装脚本集中设置环境变量，避免把密钥写入 `AYAR.yml` 或面板里：

```
#!/usr/bin/env bash
set -euo pipefail

cd /www/wwwroot/ythls-FastAPI

# 覆盖安全配置（也可放到面板“启动命令”里）
export YTHLS_REQUIRE_API_KEY=true
export YTHLS_API_KEYS="Sunkey9827,Sunkey0711"

exec /www/wwwroot/ythls-FastAPI/venv/bin/python basla.py
```

- 保存为：`/www/wwwroot/ythls-FastAPI/run.sh`
- 赋权与换行：
  - `chmod +x /www/wwwroot/ythls-FastAPI/run.sh`
  - 如从 Windows 上传：`sed -i 's/\r$//' /www/wwwroot/ythls-FastAPI/run.sh`
- 宝塔 Supervisor 配置：
  - 运行目录：`/www/wwwroot/ythls-FastAPI`
  - 启动命令：`/bin/bash /www/wwwroot/ythls-FastAPI/run.sh`
  - 自动启动/重启：开启
- 注意：如果你的虚拟环境目录不是 `venv` 而是 `.venv`，请把脚本中最后一行改为对应路径。

## 许可与鸣谢

- 许可：GPLv3（见 `LICENSE`）
- 原作者与社区：[@keyiflerolsun](https://github.com/keyiflerolsun) 与贡献者
