"""The Plash CLI tool"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['PLASH_CONFIG_HOME', 'stop', 'start', 'logs', 'get_client', 'mk_auth_req', 'get_app_id', 'endpoint', 'is_included',
           'create_tar_archive', 'validate_app', 'poll_cookies', 'login', 'deploy', 'view', 'delete', 'endpoint_func',
           'download']

# %% ../nbs/00_core.ipynb 2
from fastcore.all import *
from fastcore.xdg import *
import secrets, webbrowser, json, httpx, io, tarfile
from pathlib import Path
from uuid import uuid4
from time import time, sleep

import io, sys, tarfile

# %% ../nbs/00_core.ipynb 4
PLASH_CONFIG_HOME = xdg_config_home() / 'plash_config.json'

# %% ../nbs/00_core.ipynb 5
def get_client(cookie_file):
    client = httpx.Client()
    if not cookie_file.exists():
        raise FileNotFoundError("Plash config not found. Please run plash_login and try again.")
    cookies = Path(cookie_file).read_json()
    client.cookies.update(cookies)
    return client

# %% ../nbs/00_core.ipynb 6
def mk_auth_req(url:str, method:str='get', **kwargs): return getattr(get_client(PLASH_CONFIG_HOME), method)(url, **kwargs)

# %% ../nbs/00_core.ipynb 7
def get_app_id(path:Path):
    plash_app = Path(path) / '.plash'
    if not plash_app.exists(): raise FileNotFoundError(f"File not found: {plash_app=}")
    return parse_env(fn=plash_app)['PLASH_APP_ID']

# %% ../nbs/00_core.ipynb 8
def endpoint(path, local, port=None):
    p = "http" if local else "https"
    d = f"localhost:{port}" if local else "pla.sh"
    return f"{p}://{d}{path}"

# %% ../nbs/00_core.ipynb 9
def is_included(path):
    "Returns True if path should be included in deployment"
    if path.name.startswith('.'): return False
    if path.suffix == '.pyc': return False
    excludes = {'.git', '__pycache__', '.gitignore', '.env', 
                '.pytest_cache', '.venv', 'venv', '.ipynb_checkpoints',
                '.vscode', '.idea', '.sesskey'}
    return not any(p in excludes for p in path.parts)

# %% ../nbs/00_core.ipynb 10
def create_tar_archive(path # Path to directory containing FastHTML app
                      )->io.BytesIO: # Buffer of tar directory
    "Creates a tar archive of a directory, excluding files based on is_included"
    buf = io.BytesIO()
    files = L(Path(path).iterdir()).filter(is_included)

    with tarfile.open(fileobj=buf, mode='w:gz') as tar:
        for f in files: tar.add(f, arcname=f.name)
    buf.seek(0)
    return buf, len(files)

# %% ../nbs/00_core.ipynb 11
def validate_app(path):
    "Validates that the app in the directory `path` is deployable as a FastHTML app"
    print("Analyzing project structure...")

    main_file = Path(path) / "main.py"
    if not main_file.exists():
        print('[red bold]ERROR: Your FastHTML app must have a main.py[/red bold]')
        print(f'Your path is: [bold]{path}[/bold]')
        sys.exit(1)

# %% ../nbs/00_core.ipynb 13
def poll_cookies(paircode, local, port=None, interval=1, timeout=180):
    "Poll server for token until received or timeout"
    start = time()
    client = httpx.Client()
    url = endpoint(f"/cli_token?paircode={paircode}",local,port)
    while time()-start < timeout:
        resp = client.get(url).raise_for_status()
        if resp.text.strip(): return dict(client.cookies)
        sleep(interval)
        
@call_parse
def login(
    local:bool=False,  # Local dev
    port:int=5002      # Port for local dev
):
    "Authenticate CLI with server and save config"
    paircode = secrets.token_urlsafe(16)
    login_url = httpx.get(endpoint(f"/cli_login?paircode={paircode}",local,port)).text
    print(f"Opening browser for authentication:\n{login_url}\n")
    webbrowser.open(login_url)
    
    cookies = poll_cookies(paircode, local, port)
    if cookies:
        Path(PLASH_CONFIG_HOME).write_text(json.dumps(cookies))
        print(f"Authentication successful! Config saved to {PLASH_CONFIG_HOME}")
    else: print("Authentication timed out.")

# %% ../nbs/00_core.ipynb 15
@call_parse
def deploy(
    path:Path=Path('.'), # Path to project
    local:bool=False,    # Local dev
    port:int=5002):      # Port for local dev
    """🚀 Ship your app to production"""
    print('Initializing deployment...')
    validate_app(path)
    tarz, filecount = create_tar_archive(path)

    plash_app = Path(path) / '.plash'
    if not plash_app.exists():
        # Create the .plash file and write the app name
        plash_app.write_text(f'export PLASH_APP_ID=fasthtml-app-{str(uuid4())[:8]}')
    aid = parse_env(fn=plash_app)['PLASH_APP_ID']
    
    resp = mk_auth_req(endpoint("/upload",local,port), "post", files={'file': tarz}, timeout=300.0, data={'aid': aid})
    if resp.status_code == 200: 
        print('✅ Upload complete! Your app is currently being built.')
        if local: print(f'It will be live at http://{aid}.localhost')
        else: print(f'It will be live at https://{aid}.pla.sh')
    else:
        print(f'Failure {resp.status_code}')
        print(f'Failure {resp.text}')

# %% ../nbs/00_core.ipynb 17
@call_parse
def view(
    path:Path=Path('.'), # Path to project
    local:bool=False,    # Local dev
):
    aid = get_app_id(path)
    if local: url = f"http://{aid}.localhost"
    else: url = f"https://{aid}.pla.sh"
    print(f"Opening browser to view app :\n{url}\n")
    webbrowser.open(url)

# %% ../nbs/00_core.ipynb 19
@call_parse
def delete(
    path:Path=Path('.'), # Path to project
    local:bool=False,    # Local dev
    port:int=5002,       # Port for local dev
    force:bool=False):   # Skip confirmation prompt
    'Delete your deployed app'
    aid = get_app_id(path)
    if not force:
        confirm = input(f"Are you sure you want to delete app '{aid}'? This action cannot be undone. [y/N]: ")
        if confirm.lower() not in ['y', 'yes']:
            print("Deletion cancelled.")
            return
    
    print(f"Deleting app '{aid}'...")
    r = mk_auth_req(endpoint(f"/delete?aid={aid}",local,port), "delete")
    return r.text

# %% ../nbs/00_core.ipynb 21
def endpoint_func(endpoint_name):
    'Creates a function for a specific API endpoint'
    @call_parse
    def func(
        path:Path=Path('.'), # Path to project
        local:bool=False,    # Local dev
        port:int=5002):      # Port for local dev
        aid = get_app_id(path)
        r = mk_auth_req(endpoint(f"{endpoint_name}?aid={aid}", local, port))
        return r.text
    
    # Set the function name and docstring
    func.__name__ = endpoint_name
    func.__doc__ = f"Access the '{endpoint_name}' endpoint for your app"
    
    return func

# Create endpoint-specific functions
stop = endpoint_func('/stop')
start = endpoint_func('/start')
logs = endpoint_func('/logs')

# %% ../nbs/00_core.ipynb 23
@call_parse
def download(
    path:Path=Path('.'),                # Path to project
    save_path:Path=Path("./download/"), # Save path (optional) 
    local:bool=False,                   # Local dev
    port:int=5002,                      # Port for local dev
    ):
    'Download your deployed app.'
    aid = get_app_id(path)
    try: save_path.mkdir(exist_ok=False)
    except: print(f"ERROR: Save path ({save_path}) already exists. Please rename or delete this folder to avoid accidental overwrites.")
    else:
        response = mk_auth_req(endpoint(f'/download?aid={aid}', local, port)).raise_for_status()
        file_bytes = io.BytesIO(response.content)
        with tarfile.open(fileobj=file_bytes, mode="r:gz") as tar: tar.extractall(path=save_path)
        print(f"Downloaded your app to: {save_path}")
