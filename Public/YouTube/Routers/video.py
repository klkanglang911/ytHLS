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
    # Enforce API Key if configured
    await enforce_api_key(request)
    yt_data    = await youtube.video2data(id)
    stream_url = yt_data.get("streamUrl")
    if not stream_url:
        raise HTTPException(status_code=410, detail="HLS URL not found")

    # Direct redirect to YouTube HLS URL (works with most players like PotPlayer)
    return RedirectResponse(url=stream_url, status_code=302)

@youtube_router.get("/video/{id}.json")
@kekik_cache(ttl=CACHE_TIME, is_fastapi=True)
async def get_video_json(request: Request, id: str):
    yt_data = await youtube.video2data(id)
    if not yt_data:
        raise HTTPException(status_code=410, detail="Video not found")

    return yt_data
