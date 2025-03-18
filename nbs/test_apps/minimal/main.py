from fasthtml.common import *

app, rt = fast_app()

@rt
def index():
    return H1("Hello world!")

serve()
