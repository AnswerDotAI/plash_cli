# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "uvicorn==0.35.0",
# ]
# ///

import marimo

__generated_with = "0.14.13"
app = marimo.App(width="columns")


@app.cell
def _():
    import marimo as mo
    import uvicorn
    return mo, uvicorn


@app.cell
def _(mo):
    slider = mo.ui.slider(1, 10, 1)
    slider
    return (slider,)


@app.cell
def _(slider):
    "n" + "n".join(["a"] * slider.value) + " BATMAN!"
    return


@app.cell
def _(mo, uvicorn):
    if mo.app_meta().mode == "script":
        import marimo

        server = marimo.create_asgi_app().with_app(path="", root=__file__).build()
        uvicorn.run(server, host="0.0.0.0", port=5001)
    return


if __name__ == "__main__":
    app.run()
