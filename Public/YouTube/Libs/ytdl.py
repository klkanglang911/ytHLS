# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from CLI      import konsol
from yt_dlp   import YoutubeDL
from Core     import kekik_cache
from Settings import CACHE_TIME
import shutil

def _refresh_cookies():
    """Copy original cookies to work file before each yt-dlp call to prevent login info loss"""
    try:
        shutil.copy("cookies.txt", "cookies_work.txt")
    except Exception:
        pass

class YouTube:
    def __init__(self):
        self.ydl_opts = {
            "quiet"       : True,
            "no_warnings" : True,
            "format"      : "best",
            "cookiefile"  : "cookies_work.txt",
        }

    @kekik_cache(ttl=CACHE_TIME)
    async def __data(self, video_id: str) -> dict:
        _refresh_cookies()
        with YoutubeDL(self.ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            except Exception:
                return {}

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
        _refresh_cookies()
        with YoutubeDL(self.ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"https://www.youtube.com/channel/{channel_id}/live", download=False)
            except Exception:
                return {}

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
            _refresh_cookies()
            with YoutubeDL({**self.ydl_opts, "extract_flat": True}) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                except Exception:
                    continue

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
