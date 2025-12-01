# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

ythls-FastAPI 是一个基于 FastAPI 的 YouTube HLS 代理服务，支持获取 YouTube 视频和频道直播的 HLS 流。核心功能包括 m3u8 清单改写、媒体分片代理、API Key 安全控制。

## 开发命令

```bash
# 安装依赖
python -m pip install -r requirements.txt

# 启动开发服务器（监听 127.0.0.1:3310）
python basla.py

# Docker 运行
docker compose up -d --build
```

## 架构概览

### 入口与启动
- `basla.py` - 主入口，调用 `Core.Motor.basla()` 启动 Uvicorn
- `Core/__init__.py` - FastAPI 应用定义和路由注册
- `Core/Motor.py` - Uvicorn 启动器

### 模块结构（Public/）
| 模块 | 路由前缀 | 职责 |
|------|---------|------|
| YouTube | `/youtube` | 核心HLS代理功能 |
| OxAx | `/oxax` | 成人频道流媒体 |
| SineWix | `/sinewix` | 电影/动漫聚合（MongoDB） |
| CNBCE | `/cnbce` | 其他功能 |
| Home | `/` | 主页静态资源 |

### YouTube 模块核心流程
```
请求 → video.py/channel.py → YouTube.py或ytdl.py获取数据 → proxy.py改写m3u8 → 返回代理后的HLS流
```

关键文件：
- `Public/YouTube/Libs/YouTube.py` - HTML 解析模式（httpx+parsel）
- `Public/YouTube/Libs/ytdl.py` - yt-dlp 模式（支持 cookies.txt 登录）
- `Public/YouTube/Routers/proxy.py` - m3u8 清单改写与分片代理

### 中间件与工具（Core/Modules/）
- `_auth.py` - API Key 验证（X-API-Key 头或 k/key/api_key 参数）
- `_istek.py` - 请求日志中间件（7.5秒超时保护）
- `_IP_Log.py` - IP 地理位置查询

## 配置系统

配置文件：`AYAR.yml`（参考 `AYAR.example.yml`）

```yaml
APP:
  HOST: 127.0.0.1
  PORT: 3310
  CACHE: 15           # 缓存TTL（分钟）
yt-dlp: true          # true=yt-dlp模式，false=HTML解析模式
SECURITY:
  REQUIRE_API_KEY: false
  API_KEYS: []
```

环境变量覆盖（生产推荐）：
- `YTHLS_REQUIRE_API_KEY` - 覆盖 API Key 开关
- `YTHLS_API_KEYS` - 逗号分隔的 Key 列表

## 代码约定

### 命名风格
项目使用土耳其语变量名：
- `basla` = 启动，`hata` = 错误，`istek` = 请求，`yanit` = 响应
- `kanal` = 频道，`video` = 视频

### 缓存模式
使用 `Kekik.cache.kekik_cache` 装饰器：
```python
from Kekik.cache import kekik_cache

@kekik_cache(ttl=CACHE_TIME)
async def get_data():
    ...
```

### 异步优先
- 所有 I/O 操作使用 async/await
- HTTP 请求使用 `httpx.AsyncClient`
- MongoDB 使用 `motor.motor_asyncio.AsyncIOMotorClient`

## API 端点

YouTube 核心端点：
- `GET /youtube/video/{id}.m3u8` - 视频 HLS 流
- `GET /youtube/video/{id}.json` - 视频元数据
- `GET /youtube/channel/{id}.m3u8` - 频道直播 HLS 流
- `GET /youtube/channel/{id}.json` - 频道直播元数据
- `GET /youtube/channel/{id}/lives.json` - 频道所有直播列表
- `GET /youtube/proxy/m3u8?url=...` - 代理 m3u8 清单
- `GET /youtube/proxy/seg?url=...` - 代理媒体分片

频道多直播选择参数：`?i=序号`、`?q=关键字`、`?vid=视频ID`

## 敏感文件

以下文件不应提交到版本控制：
- `AYAR.yml` - 包含 API Keys 配置
- `cookies.txt` - yt-dlp 登录凭证
