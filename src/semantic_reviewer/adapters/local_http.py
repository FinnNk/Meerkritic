"""Own the common literal-loopback endpoint and deadline policy for local models."""

import ipaddress
import math
from urllib.parse import urlsplit


def local_endpoint(endpoint: str, timeout: float) -> str:
    """Return an HTTP literal-loopback base URL or raise ValueError before any network I/O.

    Reject credentials, paths, queries, fragments and non-finite/out-of-range
    deadlines. Callers must additionally disable proxies and redirects. This
    validates the address, not the behaviour of a separately configured local proxy.
    """
    parsed = urlsplit(endpoint)
    try:
        local = ipaddress.ip_address(parsed.hostname or "").is_loopback
        port = parsed.port
    except ValueError:
        local = False
    if (
        not local
        or port == 0
        or parsed.scheme != "http"
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
    ):
        raise ValueError(
            "llama.cpp requires an HTTP literal-loopback endpoint without credentials."
        )
    if not math.isfinite(timeout) or not 0 < timeout <= 600:
        raise ValueError("Model timeout must be between zero and 600 seconds.")
    return endpoint.rstrip("/")
