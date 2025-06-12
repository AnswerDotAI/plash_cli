from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
import uvicorn

app = Starlette()
app.mount("/", StaticFiles(directory="_docs", html=True))

uvicorn.run(app, host="0.0.0.0", port=5001)