from fasthtml.common import *
from fastcore.xtras import flexicache, mtime_policy

app = FastHTML()
cached_file_response = flexicache(mtime_policy("_docs"))(FileResponse)

@app.get("/{path:path}")
async def static(path:str): 
    if "." in path: return cached_file_response(f'_docs/{path}')
    return cached_file_response(f'_docs/{path}/index.html')

serve()