import httpx, dotenv, json, base64,os
import logging as log
import jwt
from typing import Tuple

# Plash Auth Client library, for use of Plash Apps

dotenv.load_dotenv()
log.basicConfig(level=log.INFO)

IS_DEV=True
PLASH_AUTH_SERVER_PREFIX = 'http://localhost:5002' if IS_DEV else 'https://plash.app'
PLASH_AUTH_SERVER_PATH = '/api/appauth'
PLASH_AUTH_SERVER_URL = PLASH_AUTH_SERVER_PREFIX + PLASH_AUTH_SERVER_PATH

# 4a. http wrapping of call to Plash Auth Server
def _plash_auth_url(
        plash_app_id:str,
        plash_app_secret:str,   
        app_state:bytes,        # arbitrary state, for the app to convey to itself
        required_email_pattern:str|None,
        required_hd_pattern:str|None
) -> Tuple[str,dict[str:str]]|None:
    """Returns a plash auth url, and a kv pair to add to the browser session.

    The kv pair must be placed in the user session, for login to work.
    """
    payload = {
        "plash_app_id": plash_app_id,
        "app_state_b64": base64.b64encode(app_state).decode('utf-8'),
        "required_email_pattern": required_email_pattern,
        "required_hd_pattern": required_hd_pattern,
    }
    try:
        with httpx.Client() as client:
            response = client.post(
                PLASH_AUTH_SERVER_URL,
                json=payload,
                auth=(plash_app_id, plash_app_secret)
            )
            response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx
            data = response.json()
            # Assuming endpoint returns e.g. {"url_to_follow": "...", "params_for_url": {...}}
            return data.get("url_to_follow"), data.get("params_for_url", {})
    except (httpx.HTTPError, json.JSONDecodeError) as e:
        print(f"Auth request failed: {e}")
        return None

def make_plash_signin_url(
        session:dict,
        app_state:bytes=b'',
        required_email_pattern:str|None=None,
        required_hd_pattern:str|None=None
) -> str | None:
    """Returns a Plash sign-in link.

    A Plash Sign-In link is a "Sign-In with Google" link, constructed
    such that, if the end-user signs in, Plash Auth will report the
    user's numerical Google Id (their OpenID "sub" claim), to the
    Plash App which made the link.
    """
    log.info("ENTRY: make_plash_signin_url")
    # 3. Plash client library gathers info to authenticate itself in 
    #    comunication with the plash auth server
    plash_id     = os.getenv('plash_id','dummy_plash_id')
    plash_secret = os.getenv('plash_secret','dummy_plash_sceret')
    # 4. Get the plash sign-in link from the plash auth server
    retval = _plash_auth_url(plash_id,
                             plash_secret,
                             app_state,
                             required_email_pattern,
                             required_hd_pattern)
    if not retval:
        print("error")
        return None
    # 4+X. Update the plash developer app's session with a key-value pair
    #    that the plash auth server will use to identify the associated reply
    #    from Google's auth servers.
    (url,acsrf_kv) = retval
    session.update(acsrf_kv)
    # X. Return the plash sign-in link to the plash app
    return url

class _PlashReply:
    def __init__(self,reply_str:str):
        jwt = jwt.decode(reply_str)
        self.valid = jwt.signed_by_plash_server()
        if not self.valid: return
        self.sub = jwt.payload.sub
        self.app_state = jwt.payload.app_state
        
def _parse_signin_reply_sign(reply_str) -> _PlashReply:
    return _PlashReply(reply_str).sub

def goog_id_from_signin_reply(reply_str) -> str|None:
    reply = _parse_signin_reply_sign(reply_str)


def foo():
    return "foo"

