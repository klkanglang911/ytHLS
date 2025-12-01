# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from CLI      import konsol
from yt_dlp   import YoutubeDL
from Core     import kekik_cache
from Settings import CACHE_TIME
import shutil
import uuid
import os

def _get_fresh_cookies() -> str | None:
    """Create a unique copy of cookies for each yt-dlp call to prevent save_cookies() corruption.
    Returns the path to the temporary cookie file, or None if copy fails.
    """
    temp_cookie = f"cookies_temp_{uuid.uuid4().hex[:8]}.txt"
    try:
        shutil.copy("cookies.txt", temp_cookie)
        return temp_cookie
    except Exception:
        return None  # Don't fallback to original to prevent corruption

def _cleanup_cookie(path: str | None):
    """Remove temporary cookie file after use."""
    if path and path.startswith("cookies_temp_"):
        try:
            os.remove(path)
        except Exception:
            pass

class YouTube:
    def __init__(self):
        self.base_opts = {
            "quiet"       : True,
            "no_warnings" : True,
            "format"      : "best",
        }

    @kekik_cache(ttl=CACHE_TIME)
    async def __data(self, video_id: str) -> dict:
        cookie_file = _get_fresh_cookies()
        if not cookie_file:
            return {}  # Can't proceed without cookies
        opts = {**self.base_opts, "cookiefile": cookie_file}
        try:
            with YoutubeDL(opts) as ydl:
                try:
                    info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                except Exception:
                    return {}
        finally:
            _cleanup_cookie(cookie_file)

        baslik      = info.get("title", "").rstrip("- YouTube").strip()
        author_name = info.get("uploader", None)
        m3u8_url    = info.get("url", None)

        # Windows GBK encoding workaround - skip console output for non-ASCII
        try:
            konsol.print(f"\n[yellow]{author_name} | {baslik}")
        except (UnicodeEncodeError, Exception):
            pass  # Silently skip logging on Windows encoding issues

        return {
            "authorName"  : author_name,
            "streamName"  : baslik,
            "streamThumb" : f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            "streamUrl"   : m3u8_url
        }

    @kekik_cache(ttl=CACHE_TIME)
    async def video2data(self, id: str) -> dict:
        return await self.__data(id)

    @kekik_cache(ttl=CACHE_TIME)
    async def kanal2data(self, channel_id: str) -> dict:
        cookie_file = _get_fresh_cookies()
        if not cookie_file:
            return {}  # Can't proceed without cookies
        opts = {**self.base_opts, "cookiefile": cookie_file}
        try:
            with YoutubeDL(opts) as ydl:
                try:
                    info = ydl.extract_info(f"https://www.youtube.com/channel/{channel_id}/live", download=False)
                except Exception:
                    return {}
        finally:
            _cleanup_cookie(cookie_file)

        live_video_id = info.get("id", None)

        return await self.__data(live_video_id) if live_video_id else {}

    @kekik_cache(ttl=CACHE_TIME)
    async def lives(self, channel_id: str) -> list[dict]:
        """List all current live streams for a channel using yt-dlp.
        Returns a list of dicts: {id, title, uploader, thumbnail}
        """
        # Try /streams tab first, fallback to the legacy live filter url
        urls = [
            f"https://www.youtube.com/channel/{channel_id}/streams",
            f"https://www.youtube.com/channel/{channel_id}/videos?view=2&live_view=501",
        ]

        for url in urls:
            cookie_file = _get_fresh_cookies()
            if not cookie_file:
                continue  # Skip if can't create temp cookies
            opts = {**self.base_opts, "cookiefile": cookie_file, "extract_flat": True}
            try:
                with YoutubeDL(opts) as ydl:
                    try:
                        info = ydl.extract_info(url, download=False)
                    except Exception:
                        continue
            finally:
                _cleanup_cookie(cookie_file)

            entries = info.get("entries") or []
            lives: list[dict] = []
            for e in entries:
                # yt-dlp sets live_status on some tabs; otherwise rely on 'is_live' or duration==None
                live_status = e.get("live_status")
                is_live = e.get("is_live")
                if live_status in ("is_live", "was_live") and live_status != "was_live" or is_live:
                    vid = e.get("id") or (e.get("url") or "").split("v=")[-1]
                    if not vid:
                        continue
                    lives.append({
                        "id": vid,
                        "title": e.get("title"),
                        "uploader": e.get("uploader") or e.get("uploader_id"),
                        "thumbnail": (e.get("thumbnails") or [{}])[-1].get("url") if e.get("thumbnails") else None,
                    })

            if lives:
                return lives

        return []
