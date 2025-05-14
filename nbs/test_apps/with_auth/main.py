from fasthtml.common import P,A,H1,fast_app,serve

import plashauth
from plashauth import make_plash_signin_url, goog_id_from_signin_reply

app, rt = fast_app()

@rt
def index(session):
    "Route called by browsers to get a signin link"
    url = make_plash_signin_url(session)
    return P("Signin time", A("Sign in with Google",src=url))

@rt
def signin_completed(signin_reply:str):
    "Reply by the plash service to report signin results"
    if (uid := goog_id_from_signin_reply(signin_reply)) is None:
        print(f"This is not a valid reply from Plash server")
        return P("Login failed")
    else:
        handle_signin(uid)

def handle_signin(uid:str):
    "Called by the plash service to report user signins"
    print(f"user {uid} is signed in")
    # create or lookup user

@rt
def index():
    return H1(f"Hello world! {plashauth.foo()=}")

serve()
