from fasthtml.common import *
from fasthtml.magickey import MagicKey
from plash_cli.auth import send_magiclink

db = database('data/data.db')
users = db.t.user.create(id=int, email=str, pk='id', if_not_exists=True)
passkeys = db.t.passkey.create(id=str, user_id=int, public_key=bytes, sign_count=int, pk='id', if_not_exists=True)
User,Passkey = users.dataclass(),passkeys.dataclass()

class Auth(MagicKey):
    def get_user_id(self, email):
        res = users(where="email = ?", where_args=[email])
        if res: return res[0].id
        return users.insert(User(email=email)).id
    def has_passkey(self, email):
        return bool(passkeys(where="user_id = ?", where_args=[self.get_user_id(email)]))
    def get_passkey(self, cred_id):
        try: r = passkeys[cred_id]
        except NotFoundError: return None
        return dict(email=users[r.user_id].email, public_key=r.public_key, sign_count=r.sign_count)
    def save_passkey(self, cred_id, email, public_key, sign_count):
        uid = self.get_user_id(email)
        passkeys.insert(Passkey(id=cred_id, user_id=uid, public_key=public_key, sign_count=sign_count))
    def update_passkey(self, cred_id, sign_count):
        passkeys.update(Passkey(id=cred_id, sign_count=sign_count))

def send_email(email, url): 
    res = send_magiclink(email,url)
    if res.status_code == 200: return P(f'Your magic login link has beent sent to: {email}.')
    else: return P('Something went wrong, try again later.')

app, rt = fast_app()
mk = Auth(app, send_email=send_email)

@rt('/')
def home(auth):
    u = users[auth]
    return P(f'Hello {u.email}!'), A('Log out', href='/logout')

@rt('/login')
def login(error: str=None):
    errmsg = P(error.replace('_', ' ').title(), style='color:red') if error else ''
    return Titled('Sign In', errmsg,
                Button('Sign in with Passkey', hx_post='/request_passkey_auth', target_id='scripts'),
                Hr(),
                Form(method='post', action='/send_magic_link')(
                    Input(name='email', type='email', placeholder='you@example.com'),
                    Button('Send Magic Link')),
                Div(id='scripts'))

@rt('/setup_passkey')
def setup_passkey(): return Titled('Set Up Passkey',
                            P('Set up a passkey for faster logins next time?'),
                            Button('Register Passkey', hx_post='/request_passkey_reg', target_id='scripts'),
                            Form(Button('Skip'), method='post', action='/skip_passkey_reg'),
                            Div(id='scripts'))

serve()
