import os
from fasthtml.common import *

app, rt = fast_app()

# PLASH_PRODUCTION is set automatically on Plash
in_production = os.getenv('PLASH_PRODUCTION') == '1'  

@rt
def index(): return P(f"We are in mode: {in_production=}")

serve()
