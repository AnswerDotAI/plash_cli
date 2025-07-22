import httpx,os,jwt
from pathlib import Path
from warnings import warn

from plash_cli import __version__

class PlashAuthError(Exception):
    """Raised when Plash authentication fails"""
    pass

APP_SIGNIN_PATH = "/signin_completed"

in_prod = os.getenv('PLASH_PRODUCTION', '') == '1'

AUTH_EC_PUBLIC_KEY_FILE = Path(__file__).parent / "assets" / "es256_public_key.pem"

def _plash_signin_url(email_re: str=None, hd_re: str=None):
    app_id, app_secret = os.environ['PLASH_APP_ID'], os.environ['PLASH_APP_SECRET']
    res = httpx.post(os.environ['PLASH_AUTH_URL'], json=dict(app_id=app_id, email_re=email_re, hd_re=hd_re), 
                     auth=(app_id, app_secret), headers={'X-PLASH-AUTH-VERSION': __version__}).raise_for_status().json()
    if "warning" in res: warn(res.pop('warning'))
    return res

def mk_plash_signin_url(session: dict, email_re: str=None, hd_re: str=None):
    if not in_prod: return f"{APP_SIGNIN_PATH}?signin_reply=mock-sign-in-reply"
    res = _plash_signin_url(email_re, hd_re)
    session.update(res['session_kv'])
    return res['plash_signin_url']

def _parse_jwt(reply: str) -> dict:
    "Parse JWT reply and return decoded claims or error info"
    try: decoded = jwt.decode(reply, key=open(AUTH_EC_PUBLIC_KEY_FILE,"rb").read(), algorithms=["ES256"], options=dict(verify_aud=False, verify_iss=False))
    except Exception as e: return dict(auth_id=None, valid=False, sub=None, err=f'JWT validation failed: {e}')
    return dict(auth_id=decoded.get('jti'), valid=True, sub=decoded.get('sub'), err=decoded.get('err'))

def goog_id_from_signin_reply(session: dict, reply: str) -> str|None: 
    if not in_prod: return '424242424242424242424'
    parsed = _parse_jwt(reply)
    if session['plash_auth'] != parsed['auth_id']: raise PlashAuthError("Request originated from a different browser than the one receiving the reply")
    if parsed['err']: raise PlashAuthError(f"Authentication failed: {parsed['err']}")
    return parsed['sub'] if parsed['valid'] else None