# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from .        import youtube_router
from Core     import Request, RedirectResponse, HTTPException, Response
# from Kekik.cache import kekik_cache  # Temporarily disabled for VLC testing
from ..Libs   import youtube
from Settings import CACHE_TIME
import httpx
from .proxy   import rewrite_m3u8_text, _host_allowed
from Core.Modules._auth import enforce_api_key

@youtube_router.get("/channel/{id}.m3u8")
async def get_channel_hls(request: Request, id: str):
    # Enforce API Key if configured; capture to propagate in nested URIs
    k = await enforce_api_key(request)
    # Allow explicit selection when multiple lives:
    # - via query 'vid' (video id)
    # - via index 'i' (1-based)
    # - via title contains 'q'
    q_params = dict(request.query_params)
    sel_vid = q_params.get("vid") or q_params.get("v")
    if sel_vid:
        yt_data = await youtube.video2data(sel_vid)
    else:
        # Default single-live behavior
        yt_data = await youtube.kanal2data(id)

        # If index/title specified, try list lives and pick one
        if (not yt_data.get("streamUrl")) or q_params.get("i") or q_params.get("q"):
            try:
                lives = await youtube.lives(id)
            except Exception:
                lives = []

            if lives:
                # index selection
                if q_params.get("i"):
                    try:
                        idx = max(0, int(q_params.get("i")) - 1)
                    except Exception:
                        idx = 0
                    if idx < len(lives):
                        yt_data = await youtube.video2data(lives[idx]["id"]) or yt_data
                # title contains selection
                elif q_params.get("q"):
                    key = q_params.get("q").lower()
                    for e in lives:
                        t = (e.get("title") or "").lower()
                        if key in t:
                            yt_data = await youtube.video2data(e["id"]) or yt_data
                            break

    stream_url = yt_data.get("streamUrl")
    if not stream_url:
        raise HTTPException(status_code=410, detail="HLS URL not found")

    if not _host_allowed(stream_url):
        raise HTTPException(status_code=410, detail="Upstream host not allowed")

    # 获取并改写 M3U8 内容，使后续层级与分片均走本服务代理
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.get(stream_url, follow_redirects=True)
        except Exception as e:
            raise HTTPException(status_code=410, detail=f"Error fetching M3U8: {type(e).__name__}")

    if r.status_code != 200:
        raise HTTPException(status_code=410, detail=f"Failed to fetch M3U8 content (status: {r.status_code})")

    extra_qs = f"k={k}" if k else None
    rewritten = rewrite_m3u8_text(r.text, str(r.url), extra_qs)
    return Response(content=rewritten, media_type="application/vnd.apple.mpegurl")


@youtube_router.get("/channel/{id}/lives.json")
async def list_channel_lives(request: Request, id: str):
    try:
        lives = await youtube.lives(id)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"List error: {type(e).__name__}")
    return {"channelId": id, "count": len(lives), "items": lives}

@youtube_router.get("/channel/{id}.json")
# @kekik_cache(ttl=CACHE_TIME, is_fastapi=True)  # Temporarily disabled for VLC testing
async def get_channel_json(request: Request, id: str):
    yt_data = await youtube.kanal2data(id)
    if not yt_data:
        raise HTTPException(status_code=410, detail="Channel not found")

    return yt_data
