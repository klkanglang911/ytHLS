# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from yaml import load, FullLoader
import os

with open("AYAR.yml", "r", encoding="utf-8") as yaml_dosyasi:
    AYAR = load(yaml_dosyasi, Loader=FullLoader)


def _to_bool(s: str | None, default: bool = False) -> bool:
    if s is None:
        return default
    return str(s).strip().lower() in {"1", "true", "yes", "on"}


# Optional: override security config from environment variables
# YTHLS_REQUIRE_API_KEY=true|false
# YTHLS_API_KEYS=KeyA,KeyB,KeyC
sec = AYAR.setdefault("SECURITY", {}) if isinstance(AYAR, dict) else {}
env_require = os.getenv("YTHLS_REQUIRE_API_KEY")
env_keys = os.getenv("YTHLS_API_KEYS")
if env_require is not None:
    try:
        sec["REQUIRE_API_KEY"] = _to_bool(env_require, False)
    except Exception:
        pass
if env_keys:
    try:
        parsed = [k.strip() for k in env_keys.split(",") if k.strip()]
        if parsed:
            sec["API_KEYS"] = parsed
    except Exception:
        pass


HOST       = AYAR["APP"]["HOST"]
PORT       = AYAR["APP"]["PORT"]
WORKERS    = AYAR["APP"]["WORKERS"]
CACHE_TIME = AYAR["APP"]["CACHE"] * 60
