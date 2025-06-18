### TO BE DELETED AS PLASH_CLI GETS DEPLOYED TO PRD
import httpx, dotenv, json, base64, os, jwt
from typing import Tuple
from pathlib import Path

IS_DEV = True
IN_DOCKER = False
SHOULD_CHECK_JWT = True
APP_SIGNIN_PATH = "/signin_completed"
AUTH_PATH_SIGNIN = "/request_signin"
AUTH_PATH_GOOG_REDIRECT = '/goog_redirect'
AUTH_SERVER_PREFIX = 'https://plash-dev.answer.ai'  # MAKE THIS VARIABLE BUT DISCOVER IT FROM PLASH ENV
AUTH_SERVER_PREFIX = 'http://host.docker.internal:5001' if IN_DOCKER else AUTH_SERVER_PREFIX
AUTH_SIGNIN_URL = AUTH_SERVER_PREFIX + AUTH_PATH_SIGNIN
AUTH_REDIRECT_URL = AUTH_SERVER_PREFIX + AUTH_PATH_GOOG_REDIRECT
AUTH_EC_PUBLIC_KEY_FILE = Path(__file__).parent / "assets" / "es256_public_key.pem"
SESSION_KEY = 'plash_auth'

dotenv.load_dotenv()

def _plash_auth_url(plash_app_id: str, plash_app_secret: str, required_email_pattern: str|None, required_hd_pattern: str|None) -> Tuple[str,dict[str,str]]|None:
    payload = dict(plash_app_id=plash_app_id, required_email_pattern=required_email_pattern, required_hd_pattern=required_hd_pattern)
    try:
        with httpx.Client() as client:
            response = client.post(AUTH_SIGNIN_URL, json=payload, auth=(plash_app_id, plash_app_secret))
            response.raise_for_status()
            data = response.json()
            url = data.get("plash_signin_url")
            session_kv = data.get("session_kv", {})
            return (url, session_kv) if url else None
    except (httpx.HTTPError, json.JSONDecodeError) as e:
        print(f"Auth request failed: {e}")
        return None

def make_plash_signin_url(session: dict, required_email_pattern: str|None=None, required_hd_pattern: str|None=None) -> str | None:
    plash_app_id = os.getenv('PLASH_APP_ID', '1' if IS_DEV else None)
    plash_app_secret = os.getenv('PLASH_APP_SECRET', 'dummy_plash_secret' if IS_DEV else None)
    retval = _plash_auth_url(plash_app_id, plash_app_secret, required_email_pattern, required_hd_pattern)
    if not retval: return None
    url, session_kv = retval
    session.update(session_kv)
    return url

class _PlashReply:
    def __init__(self, reply_str: str):
        try:
            if SHOULD_CHECK_JWT:
                decoded_jwt = jwt.decode(reply_str, key=open(AUTH_EC_PUBLIC_KEY_FILE,"rb").read(), algorithms=["ES256"], options=dict(verify_aud=False, verify_iss=False))
                print("JWT crypto validation succeeded")
            else:
                decoded_jwt = jwt.decode(reply_str, options=dict(verify_signature=False))
            self.authreq_id = decoded_jwt.get('jti')
            self.valid = True
            self.sub = decoded_jwt.get('sub')
            self.err = decoded_jwt.get('err')
        except Exception as e:
            print(f"JWT validation failed: {e}")
            self.authreq_id = None
            self.valid = False
            self.sub = None

def _parse_signin_reply(session, reply_str) -> str|None:
    reply = _PlashReply(reply_str)
    if session[SESSION_KEY] != reply.authreq_id:
        print("request originated from a different browser than the one receiving the reply")
        return None
    return reply.sub if reply.valid else None

def goog_id_from_signin_reply(session: dict, reply_str: str) -> str|None:
    return _parse_signin_reply(session, reply_str)
### END TO BE DELETED AS PLASH_CLI GETS DEPLOYED TO PRD

from fasthtml.common import P,A,H1,fast_app,serve
import httpx
app, rt = fast_app()

@rt
def index(session): return P("Sign in with Google", href=make_plash_signin_url(session))

@rt(APP_SIGNIN_PATH)
def plash_signin_completed(session, signin_reply: str):
    uid = goog_id_from_signin_reply(session, signin_reply)
    return P("Login failed") if uid is None else P(f"Login succeeded for user {uid}")

serve()
