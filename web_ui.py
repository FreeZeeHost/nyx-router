#!/usr/bin/env python3
import os, sys, time, hashlib, sqlite3
from datetime import datetime
try:
    import gradio as gr
except ImportError:
    print("❌ Install gradio: pip install gradio")
    sys.exit(1)

sys.path.insert(0, os.path.expanduser("~/.nyx-router"))
try:
    from core import AI_WORKERS, Router, TaskClassifier, call_ai, is_free_model
except ImportError:
    print("❌ core.py not found")
    sys.exit(1)

class ChatDB:
    def __init__(self):
        self.db_path = os.path.expanduser("~/.nyx-router/chat.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, role TEXT, content TEXT, model TEXT, cost REAL, ts TEXT)')
    
    def add(self, role, content, model="", cost=0):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('INSERT INTO history (role, content, model, cost, ts) VALUES (?,?,?,?,?)',
                         (role, content, model, cost, datetime.now().isoformat()))
            conn.commit()
    
    def get(self, limit=50):
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute('SELECT role, content, model, cost FROM history ORDER BY id DESC LIMIT ?', (limit,)).fetchall()[::-1]

def build_ui():
    db = ChatDB()
    model_choices = ["auto"] + sorted(AI_WORKERS.keys())
    
    with gr.Blocks(theme=gr.themes.Dark(primary_hue="purple"), title="🌙 NYX-ROUTER") as demo:
        gr.HTML('<h1 style="text-align:center;color:#a855f7;">🌙 NYX-ROUTER</h1><p style="text-align:center;color:#94a3b8;">47+ Models · 44 Free</p>')
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(height=500, avatar_images=("🧑", "🌙"))
                with gr.Row():
                    msg = gr.Textbox(placeholder="Type your message...", scale=4, container=False)
                    send = gr.Button("Send", variant="primary")
                with gr.Row():
                    clear = gr.Button("🗑️ Clear")
                    retry = gr.Button("🔄 Retry")
            with gr.Column(scale=2):
                model = gr.Dropdown(choices=model_choices, value="auto", label="🤖 Model")
                free = gr.Checkbox(value=True, label="🆓 Prefer Free")
                gr.Markdown("### Quick Prompts")
                gr.Examples(["Buat REST API dengan FastAPI", "Tulis kode Python untuk sorting", "Jelaskan cara kerja AI"], inputs=msg)
        
        def respond(message, history, model, free):
            if not message: return "", history
            tasks = TaskClassifier.classify(message)
            if model == "auto":
                model, _ = Router.select_best_ai(tasks, free)
            resp, cost = call_ai(model, message)
            db.add("user", message)
            db.add("assistant", resp, model, cost)
            history.append((message, resp + f"\n\n---\n🤖 {model} {'🆓' if is_free_model(model) else '💰'} | 💲 ${cost:.4f}"))
            return "", history
        
        send.click(respond, [msg, chatbot, model, free], [msg, chatbot])
        msg.submit(respond, [msg, chatbot, model, free], [msg, chatbot])
        clear.click(lambda: [], outputs=[chatbot])
    
    return demo

def main():
    print("🌙 NYX-ROUTER UI at http://localhost:7860")
    build_ui().launch(server_name="0.0.0.0", server_port=7860, share=False)

if __name__ == "__main__":
    main()
