"""HTTP wrapper with retry, timeout, UA — shared across all runners."""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

USER_AGENT = "landing-system-audit/1.0 (+https://github.com/landing-system)"
DEFAULT_TIMEOUT = 15  # seconds


def make_session() -> requests.Session:
    """requests.Session with 3 retries on 5xx + 30s connect/read timeout."""
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s


def fetch(url: str, session: requests.Session | None = None,
          method: str = "GET", allow_redirects: bool = True) -> requests.Response:
    """Fetch URL with default timeout. Caller handles exceptions."""
    if session is None:
        session = make_session()
    return session.request(method, url, timeout=DEFAULT_TIMEOUT,
                           allow_redirects=allow_redirects)
