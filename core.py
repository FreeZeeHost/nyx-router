#!/usr/bin/env python3
import os, sys, json, time, re, requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional

AI_WORKERS = {
    "lokal-kecil": {"type": "ollama", "model": "llama3.2:3b", "cost": 0, "free": True, "provider": "ollama"},
    "lokal-sedang": {"type": "ollama", "model": "qwen2.5-coder:7b", "cost": 0, "free": True, "provider": "ollama"},
    "lokal-besar": {"type": "ollama", "model": "deepseek-coder:6.7b", "cost": 0, "free": True, "provider": "ollama"},
    "openrouter-auto": {"type": "openrouter", "model": "openrouter/auto", "cost": 0, "free": True, "provider": "openrouter"},
    "openrouter-qwen": {"type": "openrouter", "model": "qwen/qwen-2.5-72b-instruct", "cost": 0, "free": True, "provider": "openrouter"},
    "openrouter-llama": {"type": "openrouter", "model": "meta-llama/llama-3.3-70b-instruct", "cost": 0, "free": True, "provider": "openrouter"},
    "groq-llama": {"type": "groq", "model": "llama-3.3-70b-versatile", "cost": 0, "free": True, "provider": "groq"},
    "gemini-flash": {"type": "google", "model": "gemini-2.0-flash-exp", "cost": 0, "free": True, "provider": "google"},
    "gemini-pro": {"type": "google", "model": "gemini-2.0-pro-exp", "cost": 0, "free": True, "provider": "google"},
    "nvidia-llama": {"type": "nvidia", "model": "meta/llama-3.1-70b-instruct", "cost": 0, "free": True, "provider": "nvidia"},
    "openai-mini": {"type": "openai", "model": "gpt-4o-mini", "cost": 0.15, "free": False, "provider": "openai"},
    "openai": {"type": "openai", "model": "gpt-4o", "cost": 5, "free": False, "provider": "openai"},
    "claude": {"type": "anthropic", "model": "claude-3-5-sonnet-20241022", "cost": 3, "free": False, "provider": "anthropic"},
}

def is_free_model(w): return AI_WORKERS.get(w, {}).get("free", False)
def get_free_models(): return [n for n,c in AI_WORKERS.items() if c.get("free", False)]

def call_ai(worker, prompt):
    config = AI_WORKERS.get(worker)
    if not config: return f"❌ Worker '{worker}' tidak ditemukan", 0
    try:
        t = config.get("type", "")
        if t == "ollama": return call_ollama(config["model"], prompt), config.get("cost", 0)
        elif t == "openrouter": return call_openrouter(config["model"], prompt), 0
        elif t == "groq": return call_groq(config["model"], prompt), 0
        elif t == "google": return call_google(config["model"], prompt), 0
        elif t == "nvidia": return call_nvidia(config["model"], prompt), 0
        elif t == "openai": return call_openai(config["model"], prompt), config.get("cost", 0)
        elif t == "anthropic": return call_anthropic(config["model"], prompt), config.get("cost", 0)
        else: return f"❌ Provider '{t}' tidak dikenal", 0
    except Exception as e: return f"❌ Error: {str(e)}", 0

def call_ollama(m, p):
    import subprocess
    r = subprocess.run(["ollama", "run", m, p], capture_output=True, text=True, timeout=120)
    return r.stdout.strip()

def call_openrouter(m, p):
    k = os.environ.get("OPENROUTER_API_KEY")
    if not k: return "❌ OPENROUTER_API_KEY tidak diset"
    r = requests.post("https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
        json={"model": m, "messages": [{"role": "user", "content": p}], "temperature": 0.7}, timeout=120)
    r.raise_for_status(); return r.json()["choices"][0]["message"]["content"]

def call_groq(m, p):
    k = os.environ.get("GROQ_API_KEY")
    if not k: return "❌ GROQ_API_KEY tidak diset"
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
        json={"model": m, "messages": [{"role": "user", "content": p}], "temperature": 0.7}, timeout=120)
    r.raise_for_status(); return r.json()["choices"][0]["message"]["content"]

def call_google(m, p):
    k = os.environ.get("GOOGLE_API_KEY")
    if not k: return "❌ GOOGLE_API_KEY tidak diset"
    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}",
        json={"contents": [{"parts": [{"text": p}]}], "generationConfig": {"temperature": 0.7}}, timeout=120)
    r.raise_for_status(); return r.json()["candidates"][0]["content"]["parts"][0]["text"]

def call_nvidia(m, p):
    k = os.environ.get("NVIDIA_API_KEY")
    if not k: return "❌ NVIDIA_API_KEY tidak diset"
    r = requests.post("https://integrate.api.nvidia.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
        json={"model": m, "messages": [{"role": "user", "content": p}], "temperature": 0.7}, timeout=120)
    r.raise_for_status(); return r.json()["choices"][0]["message"]["content"]

def call_openai(m, p):
    k = os.environ.get("OPENAI_API_KEY")
    if not k: return "❌ OPENAI_API_KEY tidak diset"
    r = requests.post("https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
        json={"model": m, "messages": [{"role": "user", "content": p}], "temperature": 0.7}, timeout=120)
    r.raise_for_status(); return r.json()["choices"][0]["message"]["content"]

def call_anthropic(m, p):
    k = os.environ.get("ANTHROPIC_API_KEY")
    if not k: return "❌ ANTHROPIC_API_KEY tidak diset"
    r = requests.post("https://api.anthropic.com/v1/messages",
        headers={"x-api-key": k, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
        json={"model": m, "max_tokens": 4096, "messages": [{"role": "user", "content": p}]}, timeout=120)
    r.raise_for_status(); return r.json()["content"][0]["text"]

class Router:
    TASK_TO_AI = {
        "coding": ["openrouter-qwen", "groq-llama", "gemini-flash", "openai"],
        "debugging": ["openrouter-qwen", "groq-llama", "gemini-pro", "openai"],
        "writing": ["openrouter-llama", "groq-llama", "gemini-flash", "openai-mini"],
        "general": ["openrouter-llama", "groq-llama", "gemini-flash", "openai-mini"],
        "simple_qa": ["lokal-kecil", "openrouter-llama", "groq-llama"],
    }
    @classmethod
    def select_best_ai(cls, task_types, prefer_free=True):
        main = task_types[0][0] if task_types else "general"
        ai_list = cls.TASK_TO_AI.get(main, ["openrouter-llama", "groq-llama", "openai-mini"])
        if prefer_free:
            free_ais = [a for a in ai_list if is_free_model(a)]
            if free_ais: return free_ais[0], 0
        return ai_list[0], AI_WORKERS.get(ai_list[0], {}).get("cost", 0)

class TaskClassifier:
    PATTERNS = {
        "coding": [r"\b(code|function|class|api|python|javascript|go|rust|java)\b"],
        "debugging": [r"\b(debug|error|fix|bug|troubleshoot)\b"],
        "writing": [r"\b(write|draft|article|blog|essay|story|email)\b"],
        "general": [r"\b(help|what is|explain|how to|bantu|tolong)\b"],
        "simple_qa": [r"^(what|who|where|when|why|how|is|are|apa|siapa|di mana|kapan|mengapa)", r"^.{0,50}$"],
    }
    @classmethod
    def classify(cls, prompt):
        results = []
        for task, patterns in cls.PATTERNS.items():
            conf = 0
            for p in patterns:
                if re.search(p, prompt, re.I): conf += 0.3
            if task == "simple_qa" and len(prompt) < 50: conf += 0.2
            if conf > 0: results.append((task, min(conf, 1.0)))
        results.sort(key=lambda x: x[1], reverse=True)
        if not results: results.append(("general", 0.5))
        return results

def mode_single(ai, prompt, prefer_free=True):
    print("\n" + "="*60)
    print("  🎯 MODE SINGLE")
    print("="*60)
    tasks = TaskClassifier.classify(prompt)
    print(f"  📋 Tugas: {tasks[0][0] if tasks else 'general'}")
    if not ai:
        ai, _ = Router.select_best_ai(tasks, prefer_free)
    print(f"  🤖 AI: {ai} {'🆓' if is_free_model(ai) else '💰'}")
    print("")
    resp, cost = call_ai(ai, prompt)
    print("─"*60)
    print(resp)
    print("─"*60)
    print(f"\n💲 Cost: ${cost:.4f}")

def mode_swarm(prompt, prefer_free=True):
    print("\n" + "="*60)
    print("  🐝 MODE SWARM")
    print("="*60)
    workers = get_free_models()[:6] if prefer_free else list(AI_WORKERS.keys())[:6]
    print(f"  🤖 AI: {', '.join(workers)}\n")
    results = {}
    with ThreadPoolExecutor(max_workers=len(workers)) as ex:
        fs = {ex.submit(call_ai, w, prompt): w for w in workers}
        for f in as_completed(fs):
            w = fs[f]
            try: results[w] = {"resp": f.result()[0], "cost": f.result()[1]}
            except: results[w] = {"resp": "❌ Error", "cost": 0}
    print("─"*60)
    print("  📊 HASIL SEMUA AI")
    print("─"*60)
    total = 0
    for w, d in results.items():
        print(f"\n🤖 {w} (${d['cost']:.4f})")
        print("─"*60)
        print(d['resp'])
        total += d['cost']
    print(f"\n💲 Total Cost: ${total:.4f}")

def mode_orchestrate(prompt, max_iter=3, prefer_free=True):
    print("\n" + "="*60)
    print("  🎼 MODE ORCHESTRATE")
    print("="*60)
    tasks = TaskClassifier.classify(prompt)
    ai, _ = Router.select_best_ai(tasks, prefer_free)
    print(f"  📋 Tugas: {tasks[0][0] if tasks else 'general'}")
    print(f"  🤖 AI awal: {ai}\n")
    last = ""
    for i in range(1, max_iter+1):
        print(f"\n{'─'*60}")
        print(f"  ITERASI {i}/{max_iter}")
        print(f"{'─'*60}")
        resp, cost = call_ai(ai, prompt)
        last = resp
        print("─"*60)
        print(resp)
        print("─"*60)
        print(f"💲 Cost: ${cost:.4f}")
        score = (1 if len(resp) > 100 else 0) + (1 if "```" in resp else 0)
        print(f"\n📊 Skor: {score}/2")
        if score >= 2:
            print("\n✅ JAWABAN LOLOS!")
            print("📝 FINAL ANSWER:")
            print("─"*60)
            print(last)
            print("─"*60)
            return
        if i == max_iter:
            print("\n⚠️ Maksimal iterasi")
            print("📝 FINAL ANSWER:")
            print("─"*60)
            print(last)
            print("─"*60)
            return
        rotation = ["openrouter-qwen", "groq-llama", "gemini-flash", "openrouter-llama"]
        ai = rotation[(rotation.index(ai) + 1) % len(rotation)] if ai in rotation else rotation[0]
        prompt = f"Feedback: Perbaiki jawaban.\nKONTEKS: {prompt}\nJAWABAN SEBELUMNYA:\n{last}\nJAWABAN BARU:"

def show_models():
    print("\n" + "="*70)
    print("  🤖 AVAILABLE MODELS")
    print("="*70)
    free = get_free_models()
    paid = [n for n,c in AI_WORKERS.items() if not c.get("free", False)]
    print(f"\n🆓 FREE ({len(free)}):")
    for m in free: print(f"  ✅ {m}")
    print(f"\n💎 PAID ({len(paid)}):")
    for m in paid: print(f"  💰 {m} - ${AI_WORKERS[m].get('cost', 0)}/1M")

def show_apis():
    print("\n" + "="*70)
    print("  🔑 FREE API KEYS")
    print("="*70)
    print("""
1. OPENROUTER_API_KEY - https://openrouter.ai/
2. GROQ_API_KEY - https://console.groq.com/
3. GOOGLE_API_KEY - https://aistudio.google.com/
4. NVIDIA_API_KEY - https://build.nvidia.com/
""")

def nyx_cli():
    import argparse
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="command")
    single = sp.add_parser("single")
    single.add_argument("prompt", nargs="*")
    single.add_argument("--ai", default="")
    single.add_argument("--free", action="store_true", default=True)
    swarm = sp.add_parser("swarm")
    swarm.add_argument("prompt", nargs="*")
    swarm.add_argument("--free", action="store_true", default=True)
    orch = sp.add_parser("orch")
    orch.add_argument("prompt", nargs="*")
    orch.add_argument("--max", type=int, default=3)
    orch.add_argument("--free", action="store_true", default=True)
    sp.add_parser("models")
    sp.add_parser("apis")
    a = p.parse_args()
    if a.command == "single":
        pr = " ".join(a.prompt)
        if pr: mode_single(a.ai if a.ai else None, pr, a.free)
        else: print("❌ Prompt wajib diisi")
    elif a.command == "swarm":
        pr = " ".join(a.prompt)
        if pr: mode_swarm(pr, a.free)
        else: print("❌ Prompt wajib diisi")
    elif a.command == "orch":
        pr = " ".join(a.prompt)
        if pr: mode_orchestrate(pr, a.max, a.free)
        else: print("❌ Prompt wajib diisi")
    elif a.command == "models": show_models()
    elif a.command == "apis": show_apis()
    else: p.print_help()

if __name__ == "__main__":
    nyx_cli()
