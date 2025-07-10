import os

# Check environment variable
plash_production = os.getenv('PLASH_PRODUCTION')

if plash_production: 
    from plash_cli.auth import make_plash_signin_url, goog_id_from_signin_reply, APP_SIGNIN_PATH
else: 
    from plash_cli.auth_mock import make_plash_signin_url, goog_id_from_signin_reply, APP_SIGNIN_PATH

from fasthtml.common import *

app, rt = fast_app()


@rt
def index(session): 
    user_id = session.get('user_id')
    if user_id:
        return Div(
            H1("Welcome to My Plash App!"),
            P(f"You are logged in as user: {user_id}"),
            A("Protected Page", href="/protected"),
            Br(), Br(),
            A("Logout", href="/logout")
        )
    else:
        return Div(
            H1("Welcome to My Plash App!"),
            P("Please sign in to access the app."),
            A("Sign in with Google", href=make_plash_signin_url(session))
        )

@rt('/protected')
def protected_page(session):
    user_id = session.get('user_id')
    if not user_id: return RedirectResponse('/', status_code=303)
    
    return Div(
        H1("Protected Page"),
        P(f"This page is only accessible to authenticated users."),
        P(f"Your user ID: {user_id}"),
        A("Back to Home", href="/")
    )

@rt('/logout')
def logout(session):
    session.clear()
    return RedirectResponse('/', status_code=303)

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

serve()
