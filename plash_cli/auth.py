import httpx, json, os, jwt, re
from typing import Tuple
from pathlib import Path
from warnings import warn

APP_SIGNIN_PATH = "/signin_completed"
AUTH_PATH_SIGNIN = "/request_signin"
AUTH_PATH_GOOG_REDIRECT = '/goog_redirect'
SESSION_KEY = 'plash_auth'

PLASH_PRODUCTION = os.getenv('PLASH_PRODUCTION', '') == '1'
AUTH_SERVER_PREFIX = os.getenv("PLASH_DOMAIN", "https://pla.sh")

AUTH_SIGNIN_URL = AUTH_SERVER_PREFIX + AUTH_PATH_SIGNIN
AUTH_REDIRECT_URL = AUTH_SERVER_PREFIX + AUTH_PATH_GOOG_REDIRECT
AUTH_EC_PUBLIC_KEY_FILE = Path(__file__).parent / "assets" / "es256_public_key.pem"

def _plash_auth_url(plash_app_id: str, plash_app_secret: str, required_email_pattern: str|None, required_hd_pattern: str|None) -> Tuple[str,dict[str,str]]|None:
    from plash_cli import __version__
    payload = dict(
        plash_app_id=plash_app_id, 
        required_email_pattern=required_email_pattern, 
        required_hd_pattern=required_hd_pattern
    )
    try:
        with httpx.Client() as client:
            client.headers.update({'X-PLASH-AUTH-VERSION': __version__})
            response = client.post(AUTH_SIGNIN_URL, json=payload, auth=(plash_app_id, plash_app_secret))
            response.raise_for_status()
            data = response.json()
            if "warning" in data: warn(data['warning'])
            url = data.get("plash_signin_url")
            session_kv = data.get("session_kv", {})
            return (url, session_kv) if url else None
    except (httpx.HTTPError, json.JSONDecodeError) as e:
        print(f"Auth request failed: {e}")
        return None

def make_plash_signin_url(session: dict, required_email_pattern: str|None=None, required_hd_pattern: str|None=None) -> str | None:
    if required_email_pattern: re.compile(required_email_pattern)
    if required_hd_pattern: re.compile(required_hd_pattern)
    plash_app_id = os.environ['PLASH_APP_ID']
    plash_app_secret = os.environ['PLASH_APP_SECRET']
    retval = _plash_auth_url(plash_app_id, plash_app_secret, required_email_pattern, required_hd_pattern)
    if not retval: return None
    url, session_kv = retval
    session.update(session_kv)
    return url

class _PlashReply:
    def __init__(self, reply_str: str):
        try:
            decoded_jwt = jwt.decode(reply_str, key=open(AUTH_EC_PUBLIC_KEY_FILE,"rb").read(), algorithms=["ES256"], options=dict(verify_aud=False, verify_iss=False))
            self.authreq_id = decoded_jwt.get('jti')
            self.valid = True
            self.sub = decoded_jwt.get('sub')
            self.err = decoded_jwt.get('err')
        except Exception as e:
            print(f"JWT validation failed: {e}")
            self.authreq_id = None
            self.valid = False
            self.sub = None

def goog_id_from_signin_reply(session: dict, reply_str: str) -> str|None: 
    reply = _PlashReply(reply_str)
    if session[SESSION_KEY] != reply.authreq_id:
        print("request originated from a different browser than the one receiving the reply")
        return None
    return reply.sub if reply.valid else None