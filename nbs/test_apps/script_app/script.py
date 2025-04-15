# /// script
# dependencies = [
#   "python-fasthtml",
# ]
# ///

from fasthtml.common import *

app, rt = fast_app()

@rt
def index():
    return H1("Hola, mundo!")

serve()
