import os
if os.getenv('IN_PRODUCTION'): from plash_cli.auth import make_plash_signin_url, goog_id_from_signin_reply, APP_SIGNIN_PATH
else: from plash_cli.auth_mock import make_plash_signin_url, goog_id_from_signin_reply, APP_SIGNIN_PATH

from fasthtml.common import *

app, rt = fast_app()

@rt
def index(session): return A("Sign in with Google", href=make_plash_signin_url(session))

@rt(APP_SIGNIN_PATH)
def plash_signin_completed(session, signin_reply: str):
    uid = goog_id_from_signin_reply(session, signin_reply)
    return P("Login failed") if uid is None else P(f"Login succeeded for user {uid}")

serve()
