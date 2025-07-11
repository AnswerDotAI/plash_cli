import os, threading, time, uuid, jwt, re
from fasthtml.common import *

APP_SIGNIN_PATH = "/signin_completed"
SESSION_KEY = 'plash_auth'
MOCK_GOOGLE_LOGIN = "/mock_google_login"
MOCK_SERVER_PORT = 8765
MOCK_SERVER_HOST = "localhost"
MOCK_SERVER_URL = f"http://{MOCK_SERVER_HOST}:{MOCK_SERVER_PORT}"

_mock_server = None
_mock_server_thread = None
_pending_auths = {}


def _start_mock_server():
    global _mock_server, _mock_server_thread
    if _mock_server is not None: return
    
    mock_app, rt = fast_app(port=MOCK_SERVER_PORT, host=MOCK_SERVER_HOST)
    
    @rt(MOCK_GOOGLE_LOGIN)
    def mock_google_login(request, auth_id: str = None, email: str = None, hd: str = None, google_id: str = None, accepts_login: str = None):
        if not auth_id or auth_id not in _pending_auths: return "Invalid auth request", 400
        auth_data = _pending_auths[auth_id]
        
        if request.method == 'POST' and email:
            import re
            accepts = accepts_login == 'true'
            if auth_data.get('required_email_pattern') and not re.match(auth_data['required_email_pattern'], email): accepts = False
            if auth_data.get('required_hd_pattern') and not re.match(auth_data['required_hd_pattern'], hd): accepts = False
            
            payload = {'jti': auth_id, 'iss': 'mock-plash-auth', 'aud': 'mock-app', 'exp': int(time.time()) + 3600, 'iat': int(time.time()), 'mock': True}
            if accepts: payload.update({'sub': google_id, 'email': email, 'hd': hd})
            else: payload['err'] = 'Authentication rejected'
            
            mock_jwt = jwt.encode(payload, 'mock-secret', algorithm='HS256')
            callback_url = f"{auth_data['callback_url']}?signin_reply={mock_jwt}"
            del _pending_auths[auth_id]
            
            return Main(H2(f"Mock Auth {'Success' if accepts else 'Failed'}"), P("Redirecting..."), 
                       Script(f"setTimeout(() => window.location.href = '{callback_url}', 2000)"))
        
        # Show form
        patterns = []
        if auth_data.get('required_email_pattern'): patterns.append(P(f"Email Pattern: {auth_data['required_email_pattern']}"))
        if auth_data.get('required_hd_pattern'): patterns.append(P(f"Domain Pattern: {auth_data['required_hd_pattern']}"))
        
        return Main(Article(H2("🧪 Mock Google Sign-In"), 
                           P("Testing Mode: Mock auth for local development"),
                           *patterns,
                           Form(Label("Email:", Input(type="email", name="email", value="test@example.com", required=True)),
                               Label("Domain:", Input(name="hd", value="example.com")),
                               Label("Google ID:", Input(name="google_id", value="123456789", required=True)),
                               Label("Result:", Select(Option("Success", value="true"), Option("Failure", value="false"), name="accepts_login")),
                               Button("Simulate Sign-In", type="submit"), 
                               method="POST", action=f"{MOCK_GOOGLE_LOGIN}?auth_id={auth_id}")))
    
    _mock_server_thread = threading.Thread(target=lambda: __import__('uvicorn').run(mock_app, host=MOCK_SERVER_HOST, port=MOCK_SERVER_PORT, log_level="error"), daemon=True)
    _mock_server_thread.start()
    _mock_server = mock_app
    time.sleep(1.0)


def make_plash_signin_url(session: dict, required_email_pattern: str | None = None, required_hd_pattern: str | None = None) -> str | None:
    if required_email_pattern: re.compile(required_email_pattern)
    if required_hd_pattern: re.compile(required_hd_pattern)
    _start_mock_server()
    auth_id = str(uuid.uuid4())
    _pending_auths[auth_id] = {'required_email_pattern': required_email_pattern, 'required_hd_pattern': required_hd_pattern, 'callback_url': f"http://localhost:5001{APP_SIGNIN_PATH}"}
    session[SESSION_KEY] = auth_id
    return f"{MOCK_SERVER_URL}{MOCK_GOOGLE_LOGIN}?auth_id={auth_id}"

def goog_id_from_signin_reply(session: dict, reply_str: str) -> str | None:
    try:
        decoded_jwt = jwt.decode(reply_str, options={"verify_signature": False})
        if session.get(SESSION_KEY) != decoded_jwt.get('jti'): return None
        if decoded_jwt.get('err'): return None
        return decoded_jwt.get('sub')
    except: return None