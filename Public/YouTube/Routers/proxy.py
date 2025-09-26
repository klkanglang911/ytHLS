# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from .        import youtube_router
from Core     import Request, HTTPException, Response
from fastapi.responses import StreamingResponse
import httpx
from urllib.parse import urlparse, urljoin, quote
import re
from Core.Modules._auth import enforce_api_key, get_api_key_from_request


ALLOWED_HOSTS = (
    "googlevideo.com",
    "youtube.com",
    "googleusercontent.com",
    "ytimg.com",
)


def _host_allowed(abs_url: str) -> bool:
    try:
        netloc = urlparse(abs_url).netloc.split(":")[0].lower()
        return any(netloc == d or netloc.endswith("." + d) for d in ALLOWED_HOSTS)
    except Exception:
        return False


def _proxify_url(path_type: str, abs_url: str, extra_qs: str | None = None) -> str:
    enc = quote(abs_url, safe="")
    if path_type == "m3u8":
        base = f"/youtube/proxy/m3u8?url={enc}"
    else:
        base = f"/youtube/proxy/seg?url={enc}"
    if extra_qs:
        joiner = '&' if ('?' in base) else '?'
        return f"{base}{joiner}{extra_qs}"
    return base


def _absolutize(base_url: str, maybe_url: str) -> str:
    try:
        if maybe_url.startswith("http://") or maybe_url.startswith("https://"):
            return maybe_url
        return urljoin(base_url, maybe_url)
    except Exception:
        return maybe_url


def rewrite_m3u8_text(content: str, base_url: str, extra_qs: str | None = None) -> str:
    lines = content.splitlines()
    out_lines: list[str] = []

    # Regex for tags containing URI="..." (EXT-X-KEY, EXT-X-MAP, EXT-X-MEDIA, etc.)
    uri_attr_re = re.compile(r'(URI=")([^\"]+)(")')

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            out_lines.append(raw_line)
            continue

        if line.startswith('#'):
            # Rewrite URI="..." attributes inside tag lines
            def _sub_uri(m):
                orig = m.group(2)
                absu = _absolutize(base_url, orig)
                if _host_allowed(absu):
                    target_type = "m3u8" if absu.lower().endswith(".m3u8") else "seg"
                    prox = _proxify_url(target_type, absu, extra_qs)
                    return m.group(1) + prox + m.group(3)
                return m.group(1) + orig + m.group(3)

            out_lines.append(uri_attr_re.sub(_sub_uri, raw_line))
            continue

        # URI line (next line after EXT-X-STREAM-INF or segment URL)
        absu = _absolutize(base_url, line)
        if _host_allowed(absu):
            target_type = "m3u8" if absu.lower().endswith(".m3u8") else "seg"
            out_lines.append(_proxify_url(target_type, absu, extra_qs))
        else:
            out_lines.append(raw_line)

    return "\n".join(out_lines) + ("\n" if content.endswith("\n") else "")


@youtube_router.get("/proxy/m3u8")
async def proxy_m3u8(request: Request, url: str | None = None, u: str | None = None):
    # Enforce API Key if configured
    await enforce_api_key(request)
    target = url or u
    if not target:
        raise HTTPException(status_code=400, detail="Missing 'url' parameter")

    if not _host_allowed(target):
        raise HTTPException(status_code=400, detail="Upstream host not allowed")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.get(target, follow_redirects=True)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Fetch error: {type(e).__name__}")

    if r.status_code != 200 or not r.text:
        raise HTTPException(status_code=503, detail="Failed to fetch upstream m3u8")

    # Propagate API key to nested URIs
    k = get_api_key_from_request(request)
    extra_qs = f"k={k}" if k else None
    rewritten = rewrite_m3u8_text(r.text, str(r.url), extra_qs)
    return Response(content=rewritten, media_type="application/vnd.apple.mpegurl")


@youtube_router.get("/proxy/seg")
async def proxy_segment(request: Request, url: str | None = None, u: str | None = None):
    # Enforce API Key if configured
    await enforce_api_key(request)
    target = url or u
    if not target:
        raise HTTPException(status_code=400, detail="Missing 'url' parameter")

    if not _host_allowed(target):
        raise HTTPException(status_code=400, detail="Upstream host not allowed")

    fwd_headers = {}
    for h in ("Range", "If-Range", "Accept", "Origin", "Referer", "User-Agent"):
        val = request.headers.get(h)
        if val:
            fwd_headers[h] = val

    if "User-Agent" not in fwd_headers:
        fwd_headers["User-Agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        )

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.get(target, headers=fwd_headers, follow_redirects=True)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Segment fetch error: {type(e).__name__}")

    resp = Response(content=r.content, status_code=r.status_code, media_type=r.headers.get("Content-Type", "application/octet-stream"))
    # Pass through useful headers for seeking
    for h in ("Content-Length", "Content-Range", "Accept-Ranges", "Cache-Control", "Expires", "Last-Modified"):
        v = r.headers.get(h)
        if v:
            resp.headers[h] = v
    return resp
