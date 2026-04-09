from fasthtml.common import *
from plash_cli.auth import *

app, rt = fast_app()

@rt
def index(session):
    if email:=session.get('email'):
        return (H1(f"Welcome! You are logged in as {email}"),
                A("Logout", href="/logout"))
    else:
        return (H1("Welcome! Please sign in."),
                A("Sign in with Email", href=mk_magickey_signin_url(session)))

@rt(signin_completed_rt)
def signin_completed(session, signin_reply: str):
    try:
        email = email_from_magickey_reply(session, signin_reply)
        session['email'] = email
        return RedirectResponse('/', status_code=303)
    except PlashAuthError as e:
        return Div(H2("Login Failed"), P(f"Error: {e}"), A("Try Again", href="/"))

@rt('/logout')
def logout(session):
    session.pop('email')
    return RedirectResponse('/', status_code=303)

serve()
