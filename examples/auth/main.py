from fasthtml.common import *
from plash_cli.auth import *

app, rt = fast_app()

@rt
def index(session):
    if uid:=session.get('uid'):   # <1>
            return (H1(f"Welcome! You are logged in as user: {uid}"), 
                    A("Logout", href="/logout"))
    else: 
        return (
            H1("Welcome! Please sign."), 
            A("Sign in with Google", href=mk_signin_url(session)))  # <2>

@rt(signin_completed_rt)  # <3>
def signin_completed(session, signin_reply: str):
    try: 
        uid = goog_id_from_signin_reply(session, signin_reply)  # <4>
        session['uid'] = uid
        return RedirectResponse('/', status_code=303)
    except PlashAuthError as e:  # <5> 
        return Div(
            H2("Login Failed"),
            P(f"There was an error signing you in: {e}"),
            A("Try Again", href="/")
        )

@rt('/logout')
def logout(session):
    session.pop('uid')  # <6>
    return RedirectResponse('/', status_code=303)

serve()
