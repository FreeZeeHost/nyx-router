#!/usr/bin/env python3
# ================================================================
#  NYX-ROUTER WEB UI v3.0
# ================================================================

import os
import sys
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple
import sqlite3

try:
    import gradio as gr
except ImportError:
    print("❌ Install gradio: pip install gradio")
    sys.exit(1)

sys.path.insert(0, os.path.expanduser("~/.nyx-router"))
try:
    from core import AI_WORKERS, Router, TaskClassifier, call_ai, is_free_model
except ImportError:
    print("❌ core.py not found. Please install NYX-ROUTER first.")
    sys.exit(1)

class ChatDB:
    def __init__(self, db_path: str = "~/.nyx-router/chat_history.db"):
        self.db_path = os.path.expanduser(db_path)
        self._init_db()
    
    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS chat_sessions (id TEXT PRIMARY KEY, name TEXT, created_at TEXT, updated_at TEXT, total_cost REAL DEFAULT 0)')
            c.execute('CREATE TABLE IF NOT EXISTS chat_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT, model_used TEXT, cost REAL, task_type TEXT, timestamp TEXT, FOREIGN KEY (session_id) REFERENCES chat_sessions(id))')
            conn.commit()
    
    def create_session(self, name: str = None) -> str:
        sid = f"chat_{int(time.time())}_{hashlib.md5(os.urandom(8)).hexdigest()[:8]}"
        name = name or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO chat_sessions (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)", (sid, name, datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
        return sid
    
    def add_message(self, sid: str, role: str, content: str, model_used: str = None, cost: float = 0, task_type: str = None):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO chat_messages (session_id, role, content, model_used, cost, task_type, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)", (sid, role, content, model_used, cost, task_type, datetime.now().isoformat()))
            if role == "assistant":
                c.execute("UPDATE chat_sessions SET total_cost = total_cost + ?, updated_at = ? WHERE id = ?", (cost, datetime.now().isoformat(), sid))
            conn.commit()
    
    def get_session_history(self, sid: str) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM chat_messages WHERE session_id = ? ORDER BY timestamp ASC", (sid,))
            return [dict(row) for row in c.fetchall()]

class NyxUI:
    def __init__(self):
        self.db = ChatDB()
        self.current_session = self.db.create_session()
    
    def process_chat(self, message: str, model: str, prefer_free: bool):
        task_types = TaskClassifier.classify(message)
        task_type = task_types[0][0] if task_types else "general"
        if model == "auto":
            model, _ = Router.select_best_ai(task_types, prefer_free)
        response, cost = call_ai(model, message)
        self.db.add_message(self.current_session, "user", message, None, 0, task_type)
        self.db.add_message(self.current_session, "assistant", response, model, cost, task_type)
        is_free = is_free_model(model)
        cost_display = "🆓 GRATIS" if is_free else f"💰 ${cost:.4f}"
        return response + f"\n\n---\n🤖 **Model**: {model} ({cost_display})\n📋 **Task**: {task_type}"

def build_ui():
    ui = NyxUI()
    model_choices = ["auto"] + sorted(AI_WORKERS.keys())
    
    with gr.Blocks(theme=gr.themes.Dark(primary_hue="purple"), title="🌙 NYX-ROUTER") as demo:
        gr.HTML("""<div style="text-align:center;padding:20px;background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:15px;margin-bottom:20px;"><h1 style="color:#a855f7;">🌙 NYX-ROUTER</h1><p style="color:#94a3b8;">General Purpose AI Router · 47+ Models · 44 Free Models</p></div>""")
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(height=500, avatar_images=("🧑", "🌙"))
                with gr.Row():
                    msg = gr.Textbox(placeholder="Type your message...", scale=4, container=False)
                    send = gr.Button("Send", variant="primary", scale=1)
                with gr.Row():
                    clear = gr.Button("🗑️ Clear", size="sm")
                    retry = gr.Button("🔄 Retry", size="sm")
            with gr.Column(scale=2):
                model = gr.Dropdown(choices=model_choices, value="auto", label="🤖 Model")
                prefer_free = gr.Checkbox(value=True, label="🆓 Prefer Free Models")
                gr.Markdown("### ⚡ Quick Prompts")
                gr.Examples(examples=["Buat REST API dengan FastAPI","Tulis kode Python","Debug error","Tulis email","Translate ke Indonesian","Research tentang AI"], inputs=msg)
        
        def respond(message, history, model, prefer_free):
            if not message: return "", history
            response = ui.process_chat(message, model, prefer_free)
            history.append((message, response))
            return "", history
        
        send.click(respond, [msg, chatbot, model, prefer_free], [msg, chatbot])
        msg.submit(respond, [msg, chatbot, model, prefer_free], [msg, chatbot])
        clear.click(lambda: [], outputs=[chatbot])
    
    return demo

def main():
    print("🌙 NYX-ROUTER Web UI v3.0")
    print("   Open http://localhost:7860")
    print("   47+ Models, 44 Free Models")
    build_ui().launch(server_name="0.0.0.0", server_port=7860, share=False)

if __name__ == "__main__":
    main()
