from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root(): return {"Hello": "World"}

uvicorn.run(app, host="0.0.0.0", port=5001)
