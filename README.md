# plash-cli


<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

**WARNING** - Plash is in Beta and we have released it in its
semi-stable state to gather early feedback to improve. We do not
recommend hosting critical applications yet.

## Usage

### Installation

Install latest from the GitHub
[repository](https://github.com/AnswerDotAI/plash-cli):

``` sh
$ pip install git+https://github.com/AnswerDotAI/plash-cli.git
```

or from [pypi](https://pypi.org/project/plash-cli/)

``` sh
$ pip install plash-cli
```

## Deploy Your First FastHTML App

### Set Up Your Plash Token

You’ll need to set a PLASH_TOKEN and PLASH_EMAIL environment variables
to use Plash. To obtain these, do the following:

1.  Signup for an account at https://pla.sh/
2.  Activate your Plash subscription
3.  Follow instructions in your Plash dashboard to save credentials
    locally

### Create a FastHTML App

Create a directory for your FastHTML app, and go into it:

``` sh
mkdir minimal
cd minimal
```

Create `main.py` containing:

``` python
from fasthtml.common import *

app, rt = fast_app()

@rt
def index():
    return H1("Hello world!")

serve()
```

Then create a requirements.txt containing:

    python-fasthtml

### Deploy your app

Run `plash_deploy`. Your app will be live at
`https://<app-name>.pla.sh`. The URL will be shown in the deployment
output.

### App Dependencies

If your app needs additional dependencies to run, we offer a number of
ways to have them included in your deployed app.

#### Python Dependencies

To have python dependencies installed in your deployed app, you can
provide a `requirements.txt` and it will be pip installed. By default,
all deployed apps have fasthtml as a dependency.

#### Non-Python Dependencies

For any other depencies of setup processes, you can provide a `setup.sh`
which will be executed during the build step of your app. For example,
you can use this to install apt packages (this is ran as root in your
apps container, so omit any `sudo`):

``` bash
#!/bin/bash
apt install <package_name>
```

#### Env Variables

If your app depends on secrets or other types of environment variables,
you can have them available in your deployed app by providing a
`plash.env`, which will be sourced during your apps startup. Here is an
example:

    export MY_ENV_VARIABLE=hijkl
    export ANOTHER_SECRET=abcdef

Inside of your running container, we automatically set an environment
variable (`PLASH_PRODUCTION=1`) so you are able to use it for checking
if your application is inside a Plash deployment or not.

## Databases

For apps that use persistent storage, we recommend sqlite. The docker
container your app runs in has a working directory of /app which is a
volume mounted to a folder that we hourly backup. Therefore, we
recommend placing your sqlite database somewhere in that directory. Note
when redeploying an app with plash_deploy, we automatically overwrite
existing files with the same name as those uploaded. Therefore to
prevent data loss, ensure any local database files do not clash with any
deployed database names that your app may set up. You can use the
environment variable `PLASH_PRODUCTION`, which we automatically set to 1
in your Plash container, to modify your apps behavior for local and
production development. You can download any deployed database names by
clicking the Download App button to get a compressed file of all files
in your /app folder in your deployed app.

## Deploy to Pla.sh on commit

```yaml
yaml 
name: Deploy to Plash

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: Create Plash config
        run: |
          mkdir -p ~/.config
          echo "PLASH_EMAIL=${{ secrets.PLASH_EMAIL }}" > ~/.config/plash.env
          echo "PLASH_TOKEN=${{ secrets.PLASH_TOKEN }}" >> ~/.config/plash.env

      - name: Install plash_cli with uv
        run: pip install plash_cli

      - name: Deploy to Plash
        run: plash_deploy
```