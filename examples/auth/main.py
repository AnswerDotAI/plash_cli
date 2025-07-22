import os
from fasthtml.common import *
from plash_cli.auth import *

IN_PROD = os.getenv('PLASH_PRODUCTION')
app, rt = fast_app()

@rt
def index(session): 
    user_id = session.get('user_id')
    if user_id:
        return Div(
            H1("Welcome to My Plash App!"),
            P(f"You are logged in as user: {user_id}"),
            A("Logout", href="/logout")
        )
    else:
        return Div(
            H1("Welcome to My Plash App!"),
            P("Please sign in to access the app."),
            A("Sign in with Google", href=mk_plash_signin_url(session))
        )

@rt(APP_SIGNIN_PATH)
def plash_signin_completed(session, signin_reply: str):
    uid = goog_id_from_signin_reply(session, signin_reply)
    if uid is None:
        return Div(
            H2("Login Failed"),
            P("There was an error signing you in. Please try again."),
            A("Try Again", href="/")
        )
    else:
        session['user_id'] = uid
        return RedirectResponse('/', status_code=303)

@rt('/logout')
def logout(session):
    session.pop('user_id', None)
    return RedirectResponse('/', status_code=303)

serve()