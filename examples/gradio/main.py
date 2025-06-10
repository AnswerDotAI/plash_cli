import gradio as gr

def greet(name): return f"Hello {name}!"

gr.Interface(greet, "text", "text").launch(server_port=5001, server_name="0.0.0.0") 