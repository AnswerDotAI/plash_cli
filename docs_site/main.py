from fasthtml.common import *
from asyncstdlib.functools import cache

app = FastHTML()

@app.get("/{path:path}")
@cache
async def static(path:str): 
    if "." not in path: path += "/index.html"
    return FileResponse(f'_docs/{path}')

serve()