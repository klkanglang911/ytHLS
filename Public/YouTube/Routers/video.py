# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from .        import youtube_router
from Core     import Request, RedirectResponse, HTTPException, kekik_cache, Response
from ..Libs   import youtube
from Settings import CACHE_TIME
import httpx
from .proxy   import rewrite_m3u8_text, _host_allowed
from Core.Modules._auth import enforce_api_key

@youtube_router.get("/video/{id}.m3u8")
async def get_video_hls(request: Request, id: str):
    # Enforce API Key if configured; capture to propagate
    k = await enforce_api_key(request)
    yt_data    = await youtube.video2data(id)
    stream_url = yt_data.get("streamUrl")
    if not stream_url:
        raise HTTPException(status_code=410, detail="HLS URL not found")

    if not _host_allowed(stream_url):
        raise HTTPException(status_code=410, detail="Upstream host not allowed")

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

@youtube_router.get("/video/{id}.json")
@kekik_cache(ttl=CACHE_TIME, is_fastapi=True)
async def get_video_json(request: Request, id: str):
    yt_data = await youtube.video2data(id)
    if not yt_data:
        raise HTTPException(status_code=410, detail="Video not found")

    return yt_data
