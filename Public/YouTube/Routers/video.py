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
    print(f"[DEBUG] m3u8 request for video: {id}")
    # Enforce API Key if configured
    try:
        await enforce_api_key(request)
        print(f"[DEBUG] API key check passed")
    except HTTPException as e:
        print(f"[DEBUG] API key check failed: {e.status_code} - {e.detail}")
        raise HTTPException(status_code=410, detail=f"Auth error: {e.detail}")
    except Exception as e:
        print(f"[DEBUG] Unexpected error in enforce_api_key: {type(e).__name__}: {e}")
        # Continue without auth check on unexpected errors

    yt_data = await youtube.video2data(id)
    print(f"[DEBUG] yt_data: {yt_data}")
    stream_url = yt_data.get("streamUrl")
    print(f"[DEBUG] stream_url: {stream_url[:50] if stream_url else 'None'}")
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
