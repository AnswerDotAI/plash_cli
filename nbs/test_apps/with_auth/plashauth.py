import httpx
import dotenv
import jwt

from typing import Tuple

ACSRF_KEY = 'acsrf'
APP_STATE_KEY = 'app_state'

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
    # prove to the plash server which app we are
    header = {"Basic Authentication":
              f"{plash_app_id}:{plash_app_secret}"}
    payload = {"plash_app_id":plash_app_id,
               APP_STATE_KEY:app_state,
               "email_pat":required_email_pattern,
               "hd_pat":required_hd_pattern}
    plash_server_url = "https://plash.com/api/"
    res = httpx.post(plash_server_url,header, payload)
    def parse_plash_server_result(r) -> Tuple[str,dict[str:str]]:
        return ("",{ACSRF_KEY:"123"})
    if res:
        return parse_plash_server_result(res)
    else:
        print("error")
        return None

def make_plash_signin_url(
        session:dict,
        app_state:bytes=b'',
        required_email_pattern:str|None=None,
        required_hd_pattern:str|None=None
) -> str | None:
    return "URL will go here"


def make_plash_signin_url_new(
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
    # 3. Plash client library gathers info to authenticate itself in 
    #    comunication with the plash auth server
    plash_id     = dotenv.get('plash_id')
    plash_secret = dotenv.get('plash_secret')
    # 4. Get the plash sign-in link from the plash auth server
    retval = _plash_auth_url(plash_id,
                             plash_secret,
                             app_state,
                             required_email_pattern,
                             required_hd_pattern)
    if not retval:
        print("error")
        return None
    # X. Update the plash developer app's session with a key-value pair
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

