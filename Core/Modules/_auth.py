# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from fastapi import HTTPException, Request
from Settings import AYAR


def _security_cfg():
    return (AYAR.get("SECURITY") or {}) if isinstance(AYAR, dict) else {}


def api_key_required() -> bool:
    cfg = _security_cfg()
    return bool(cfg.get("REQUIRE_API_KEY", False))


def allowed_api_keys() -> set[str]:
    cfg = _security_cfg()
    keys = cfg.get("API_KEYS") or []
    try:
        return {str(k) for k in keys}
    except Exception:
        return set()


def get_api_key_from_request(request: Request) -> str | None:
    # Header first
    key = request.headers.get("X-API-Key")
    if key:
        return key.strip()
    # Query fallbacks
    q = request.query_params
    for name in ("k", "key", "api_key", "apikey"):
        if name in q and q.get(name):
            return q.get(name)
    return None


async def enforce_api_key(request: Request) -> str | None:
    print(f"[DEBUG AUTH] api_key_required() = {api_key_required()}")
    print(f"[DEBUG AUTH] _security_cfg() = {_security_cfg()}")
    if not api_key_required():
        # Not required; allow but return provided key if any (to propagate)
        return get_api_key_from_request(request)

    provided = get_api_key_from_request(request)
    if not provided:
        raise HTTPException(status_code=401, detail="API Key required")

    if provided not in allowed_api_keys():
        raise HTTPException(status_code=403, detail="Invalid API Key")

    return provided

