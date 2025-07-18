import httpx,json,os,jwt,re
from typing import Tuple
from pathlib import Path
from warnings import warn

class PlashAuthError(Exception):
    """Raised when Plash authentication fails"""
    pass

APP_SIGNIN_PATH = "/signin_completed"
AUTH_PATH_SIGNIN = "/request_signin"
AUTH_PATH_GOOG_REDIRECT = '/goog_redirect'
SESSION_KEY = 'plash_auth'

PLASH_PRODUCTION = os.getenv('PLASH_PRODUCTION', '') == '1'
AUTH_SERVER_PREFIX = os.getenv("PLASH_DOMAIN", "https://auth.pla.sh")

AUTH_SIGNIN_URL = AUTH_SERVER_PREFIX + AUTH_PATH_SIGNIN
AUTH_REDIRECT_URL = AUTH_SERVER_PREFIX + AUTH_PATH_GOOG_REDIRECT
AUTH_EC_PUBLIC_KEY_FILE = Path(__file__).parent / "assets" / "es256_public_key.pem"

def _plash_auth_url(app_id: str, app_secret: str, email_pat: str|None, hd_pat: str|None) -> Tuple[str,dict[str,str]]|None:
    from plash_cli import __version__
    payload = dict(plash_app_id=app_id, required_email_pattern=email_pat, required_hd_pattern=hd_pat)
    try:
        with httpx.Client() as client:
            client.headers.update({'X-PLASH-AUTH-VERSION': __version__})
            response = client.post(AUTH_SIGNIN_URL, json=payload, auth=(app_id, app_secret))
            response.raise_for_status()
            data = response.json()
            if "warning" in data: warn(data['warning'])
            url = data.get("plash_signin_url")
            session_kv = data.get("session_kv", {})
            return (url, session_kv) if url else None
    except (httpx.HTTPError, json.JSONDecodeError) as e:
        print(f"Auth request failed: {e}")
        return None

def mk_plash_signin_url(session: dict, email_pat: str|None=None, hd_pat: str|None=None) -> str | None:
    if email_pat: re.compile(email_pat)
    if hd_pat: re.compile(hd_pat)
    app_id,app_secret = os.environ['PLASH_APP_ID'],os.environ['PLASH_APP_SECRET']
    retval = _plash_auth_url(app_id, app_secret, email_pat, hd_pat)
    if not retval: return None
    url, session_kv = retval
    session.update(session_kv)
    return url

def _parse_jwt(reply: str) -> dict:
    "Parse JWT reply and return decoded claims or error info"
    try:
        decoded = jwt.decode(reply, key=open(AUTH_EC_PUBLIC_KEY_FILE,"rb").read(), algorithms=["ES256"], options=dict(verify_aud=False, verify_iss=False))
        return dict(auth_id=decoded.get('jti'), valid=True, sub=decoded.get('sub'), err=decoded.get('err'))
    except Exception as e:
        return dict(auth_id=None, valid=False, sub=None, err=str(e))

def signin_reply2goog_id(session: dict, reply: str) -> str|None: 
    parsed = _parse_jwt(reply)
    if session[SESSION_KEY] != parsed['auth_id']: raise PlashAuthError("Request originated from a different browser than the one receiving the reply")
    if parsed['err']: raise PlashAuthError(f"Authentication failed: {parsed['err']}")
    return parsed['sub'] if parsed['valid'] else None