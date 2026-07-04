#!/usr/bin/env python3
# ================================================================
#  NYX-ROUTER v2.2.0 - All Free Providers
#  47+ Models, 44 Free Models, 14 Providers
# ================================================================

import os
import sys
import json
import time
import sqlite3
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import requests
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==================== AI WORKERS - ALL FREE PROVIDERS ====================

AI_WORKERS = {}

# ========== 1. OLLAMA (Lokal) - Unlimited Free ==========
AI_WORKERS.update({
    "lokal-kecil": {"type": "ollama", "model": "llama3.2:3b", "cost": 0, "strength": ["simple_qa", "translation", "summarization"], "provider": "ollama", "free": True, "limit": "Unlimited"},
    "lokal-sedang": {"type": "ollama", "model": "qwen2.5-coder:7b", "cost": 0, "strength": ["coding", "writing", "general"], "provider": "ollama", "free": True, "limit": "Unlimited"},
    "lokal-besar": {"type": "ollama", "model": "deepseek-coder:6.7b", "cost": 0, "strength": ["coding", "debugging", "data_analysis"], "provider": "ollama", "free": True, "limit": "Unlimited"}
})

# ========== 2. OPENROUTER - 20+ Free Models ==========
AI_WORKERS.update({
    "openrouter-auto": {"type": "openrouter", "model": "openrouter/auto", "cost": 0, "strength": ["coding", "general", "writing", "research"], "provider": "openrouter", "free": True, "limit": "50-1000 req/day", "note": "Auto-rute ke best free model"},
    "openrouter-gpt-oss": {"type": "openrouter", "model": "openai/gpt-oss-120b", "cost": 0, "strength": ["coding", "research", "general"], "provider": "openrouter", "free": True, "limit": "50-1000 req/day"},
    "openrouter-qwen": {"type": "openrouter", "model": "qwen/qwen-2.5-72b-instruct", "cost": 0, "strength": ["coding", "reasoning", "long-context"], "provider": "openrouter", "free": True, "limit": "50-1000 req/day"},
    "openrouter-llama": {"type": "openrouter", "model": "meta-llama/llama-3.3-70b-instruct", "cost": 0, "strength": ["coding", "general", "writing"], "provider": "openrouter", "free": True, "limit": "50-1000 req/day"},
    "openrouter-mistral": {"type": "openrouter", "model": "mistralai/mistral-7b-instruct", "cost": 0, "strength": ["general", "quick", "translation"], "provider": "openrouter", "free": True, "limit": "50-1000 req/day"},
    "openrouter-nemotron": {"type": "openrouter", "model": "nvidia/nemotron-4-340b-instruct", "cost": 0, "strength": ["coding", "agentic", "long-context"], "provider": "openrouter", "free": True, "limit": "50-1000 req/day", "note": "1M context, agentic"},
    "openrouter-gemma": {"type": "openrouter", "model": "google/gemma-2-27b-it", "cost": 0, "strength": ["general", "writing", "reasoning"], "provider": "openrouter", "free": True, "limit": "50-1000 req/day"}
})

# ========== 3. GROQ - Super Cepat ==========
AI_WORKERS.update({
    "groq-llama": {"type": "groq", "model": "llama-3.3-70b-versatile", "cost": 0, "strength": ["coding", "general", "fast", "reasoning"], "provider": "groq", "free": True, "limit": "30 RPM, 14.4K req/day", "note": "500+ tok/s"},
    "groq-gemma": {"type": "groq", "model": "gemma2-9b-it", "cost": 0, "strength": ["general", "fast"], "provider": "groq", "free": True, "limit": "30 RPM, 14.4K req/day"},
    "groq-mixtral": {"type": "groq", "model": "mixtral-8x7b-32768", "cost": 0, "strength": ["coding", "reasoning", "fast"], "provider": "groq", "free": True, "limit": "30 RPM, 14.4K req/day"},
    "groq-llama3.1": {"type": "groq", "model": "llama-3.1-70b-versatile", "cost": 0, "strength": ["coding", "general"], "provider": "groq", "free": True, "limit": "30 RPM, 14.4K req/day"}
})

# ========== 4. GOOGLE GEMINI - 1M Context ==========
AI_WORKERS.update({
    "gemini-flash": {"type": "google", "model": "gemini-2.0-flash-exp", "cost": 0, "strength": ["coding", "general", "long-context", "fast"], "provider": "google", "free": True, "limit": "15 RPM, 1.5K req/day", "note": "1M context window"},
    "gemini-flash-lite": {"type": "google", "model": "gemini-2.0-flash-lite-preview", "cost": 0, "strength": ["coding", "general"], "provider": "google", "free": True, "limit": "15 RPM, 1.5K req/day"},
    "gemini-pro": {"type": "google", "model": "gemini-2.0-pro-exp", "cost": 0, "strength": ["coding", "reasoning", "research", "long-context"], "provider": "google", "free": True, "limit": "10 RPM, 1K req/day", "note": "1M context, premium quality"}
})

# ========== 5. NVIDIA NIM - 27 Models ==========
AI_WORKERS.update({
    "nvidia-llama": {"type": "nvidia", "model": "meta/llama-3.1-70b-instruct", "cost": 0, "strength": ["coding", "general", "reasoning"], "provider": "nvidia", "free": True, "limit": "~40 RPM", "note": "27 coding models available"},
    "nvidia-mistral": {"type": "nvidia", "model": "mistralai/mixtral-8x7b-instruct", "cost": 0, "strength": ["coding", "general", "fast"], "provider": "nvidia", "free": True, "limit": "~40 RPM"},
    "nvidia-qwen": {"type": "nvidia", "model": "qwen/qwen2.5-72b-instruct", "cost": 0, "strength": ["coding", "reasoning"], "provider": "nvidia", "free": True, "limit": "~40 RPM"},
    "nvidia-nemotron": {"type": "nvidia", "model": "nvidia/nemotron-4-340b-instruct", "cost": 0, "strength": ["coding", "agentic", "long-context"], "provider": "nvidia", "free": True, "limit": "~40 RPM"}
})

# ========== 6. CEREBRAS - Tercepat ==========
AI_WORKERS.update({
    "cerebras-llama": {"type": "cerebras", "model": "llama3.3-70b", "cost": 0, "strength": ["coding", "general", "fast", "reasoning"], "provider": "cerebras", "free": True, "limit": "30 RPM, 1M token/day", "note": "500+ tok/s"},
    "cerebras-gemma": {"type": "cerebras", "model": "gemma-7b", "cost": 0, "strength": ["general", "fast"], "provider": "cerebras", "free": True, "limit": "30 RPM, 1M token/day"}
})

# ========== 7. MISTRAL - Free Tier ==========
AI_WORKERS.update({
    "mistral-codestral": {"type": "mistral", "model": "codestral-latest", "cost": 0, "strength": ["coding", "debugging", "refactoring"], "provider": "mistral", "free": True, "limit": "30 RPM, 2K req/day"},
    "mistral-small": {"type": "mistral", "model": "mistral-small-latest", "cost": 0, "strength": ["coding", "general"], "provider": "mistral", "free": True, "limit": "30 RPM, 2K req/day"},
    "mistral-large": {"type": "mistral", "model": "mistral-large-latest", "cost": 0, "strength": ["coding", "reasoning", "research"], "provider": "mistral", "free": True, "limit": "30 RPM, 2K req/day"}
})

# ========== 8. CLOUDFLARE - 16 Models ==========
AI_WORKERS.update({
    "cloudflare-llama": {"type": "cloudflare", "model": "@cf/meta/llama-3.1-8b-instruct", "cost": 0, "strength": ["coding", "general", "fast"], "provider": "cloudflare", "free": True, "limit": "10K neurons/day, 300 RPM"},
    "cloudflare-gemma": {"type": "cloudflare", "model": "@cf/google/gemma-2b-it-lora", "cost": 0, "strength": ["general", "quick"], "provider": "cloudflare", "free": True, "limit": "10K neurons/day, 300 RPM"},
    "cloudflare-mistral": {"type": "cloudflare", "model": "@cf/mistral/mistral-7b-instruct-v0.1", "cost": 0, "strength": ["coding", "general"], "provider": "cloudflare", "free": True, "limit": "10K neurons/day, 300 RPM"}
})

# ========== 9. GITHUB MODELS (Beta) - 15 Models ==========
AI_WORKERS.update({
    "github-gpt4o": {"type": "github", "model": "gpt-4o", "cost": 0, "strength": ["coding", "reasoning", "general"], "provider": "github", "free": True, "limit": "Tergantung tier", "note": "GitHub Models beta"},
    "github-gpt4o-mini": {"type": "github", "model": "gpt-4o-mini", "cost": 0, "strength": ["general", "quick"], "provider": "github", "free": True, "limit": "Tergantung tier"},
    "github-llama": {"type": "github", "model": "meta-llama-3.1-8b-instruct", "cost": 0, "strength": ["coding", "general"], "provider": "github", "free": True, "limit": "Tergantung tier"}
})

# ========== 10. HUGGINGFACE - Free Inference ==========
AI_WORKERS.update({
    "hf-llama": {"type": "huggingface", "model": "meta-llama/Llama-3.2-3B-Instruct", "cost": 0, "strength": ["coding", "general"], "provider": "huggingface", "free": True, "limit": "Rate limited"},
    "hf-mistral": {"type": "huggingface", "model": "mistralai/Mistral-7B-Instruct-v0.3", "cost": 0, "strength": ["coding", "general"], "provider": "huggingface", "free": True, "limit": "Rate limited"},
    "hf-qwen": {"type": "huggingface", "model": "Qwen/Qwen2.5-7B-Instruct", "cost": 0, "strength": ["coding", "reasoning"], "provider": "huggingface", "free": True, "limit": "Rate limited"}
})

# ========== 11. OVHCLOUD - No API Key ==========
AI_WORKERS.update({
    "ovh-llama": {"type": "ovh", "model": "Meta-Llama-3.1-70B-Instruct", "cost": 0, "strength": ["coding", "general", "reasoning"], "provider": "ovh", "free": True, "limit": "2 req/min", "note": "No API key required"},
    "ovh-mistral": {"type": "ovh", "model": "Mistral-7B-Instruct-v0.3", "cost": 0, "strength": ["coding", "general"], "provider": "ovh", "free": True, "limit": "2 req/min", "note": "No API key required"}
})

# ========== 12. LLM7 - No API Key ==========
AI_WORKERS.update({
    "llm7-gpt4o-mini": {"type": "llm7", "model": "gpt-4o-mini", "cost": 0, "strength": ["general", "quick"], "provider": "llm7", "free": True, "limit": "Shared free tier", "note": "No API key required"},
    "llm7-llama": {"type": "llm7", "model": "llama-70b", "cost": 0, "strength": ["coding", "general"], "provider": "llm7", "free": True, "limit": "Shared free tier", "note": "No API key required"}
})

# ========== 13. PREMIUM (Fallback) - Berbayar ==========
AI_WORKERS.update({
    "openai-mini": {"type": "openai", "model": "gpt-4o-mini", "cost": 0.15, "strength": ["general", "writing", "translation", "summarization"], "provider": "openai", "free": False},
    "openai": {"type": "openai", "model": "gpt-4o", "cost": 5, "strength": ["coding", "debugging", "architecture", "research", "data_analysis"], "provider": "openai", "free": False},
    "claude": {"type": "anthropic", "model": "claude-3-5-sonnet-20241022", "cost": 3, "strength": ["coding", "debugging", "architecture", "research", "writing"], "provider": "anthropic", "free": False}
})

# ==================== HELPER FUNCTIONS ====================

def is_free_model(worker: str) -> bool:
    config = AI_WORKERS.get(worker, {})
    return config.get("free", False) or config.get("cost", 1) == 0

def get_free_models() -> List[str]:
    return [name for name, config in AI_WORKERS.items() if is_free_model(name)]

def get_paid_models() -> List[str]:
    return [name for name, config in AI_WORKERS.items() if not is_free_model(name)]

# ==================== CALL AI ====================

def call_ai(worker: str, prompt: str) -> Tuple[str, float]:
    config = AI_WORKERS.get(worker)
    if not config:
        return f"❌ Worker '{worker}' tidak ditemukan", 0
    
    try:
        provider = config.get("type", "")
        
        if provider == "ollama":
            response = call_ollama(config["model"], prompt)
        elif provider == "openrouter":
            response = call_openrouter(config["model"], prompt)
        elif provider == "groq":
            response = call_groq(config["model"], prompt)
        elif provider == "google":
            response = call_google(config["model"], prompt)
        elif provider == "nvidia":
            response = call_nvidia(config["model"], prompt)
        elif provider == "cerebras":
            response = call_cerebras(config["model"], prompt)
        elif provider == "mistral":
            response = call_mistral(config["model"], prompt)
        elif provider == "cloudflare":
            response = call_cloudflare(config["model"], prompt)
        elif provider == "github":
            response = call_github(config["model"], prompt)
        elif provider == "huggingface":
            response = call_huggingface(config["model"], prompt)
        elif provider == "ovh":
            response = call_ovh(config["model"], prompt)
        elif provider == "llm7":
            response = call_llm7(config["model"], prompt)
        elif provider == "openai":
            response = call_openai(config["model"], prompt)
        elif provider == "anthropic":
            response = call_anthropic(config["model"], prompt)
        else:
            return f"❌ Provider '{provider}' tidak dikenal", 0
        
        return response, config.get("cost", 0)
    except Exception as e:
        return f"❌ Error: {str(e)}", 0

# ==================== PROVIDER IMPLEMENTATIONS ====================

def call_ollama(model: str, prompt: str) -> str:
    import subprocess
    result = subprocess.run(["ollama", "run", model, prompt], capture_output=True, text=True, timeout=120)
    return result.stdout.strip()

def call_openrouter(model: str, prompt: str) -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return "❌ OPENROUTER_API_KEY tidak diset. Daftar di https://openrouter.ai/"
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "HTTP-Referer": "https://nyx-router.local", "X-Title": "NYX-ROUTER"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 4096}
    response = requests.post(url, headers=headers, json=data, timeout=120)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def call_groq(model: str, prompt: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "❌ GROQ_API_KEY tidak diset. Daftar di https://console.groq.com/"
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 4096}
    response = requests.post(url, headers=headers, json=data, timeout=120)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def call_google(model: str, prompt: str) -> str:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "❌ GOOGLE_API_KEY tidak diset. Daftar di https://aistudio.google.com/"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096}}
    response = requests.post(url, headers=headers, json=data, timeout=120)
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

def call_nvidia(model: str, prompt: str) -> str:
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        return "❌ NVIDIA_API_KEY tidak diset. Daftar di https://build.nvidia.com/"
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 4096}
    response = requests.post(url, headers=headers, json=data, timeout=120)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def call_cerebras(model: str, prompt: str) -> str:
    api_key = os.environ.get("CEREBRAS_API_KEY")
    if not api_key:
        return "❌ CEREBRAS_API_KEY tidak diset. Daftar di https://cloud.cerebras.ai/"
    url = "https://api.cerebras.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 4096}
    response = requests.post(url, headers=headers, json=data, timeout=120)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def call_mistral(model: str, prompt: str) -> str:
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        return "❌ MISTRAL_API_KEY tidak diset. Daftar di https://console.mistral.ai/"
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 4096}
    response = requests.post(url, headers=headers, json=data, timeout=120)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def call_cloudflare(model: str, prompt: str) -> str:
    api_key = os.environ.get("CLOUDFLARE_API_KEY")
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    if not api_key or not account_id:
        return "❌ CLOUDFLARE_API_KEY atau CLOUDFLARE_ACCOUNT_ID tidak diset"
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"messages": [{"role": "user", "content": prompt}], "max_tokens": 4096}
    response = requests.post(url, headers=headers, json=data, timeout=120)
    response.raise_for_status()
    return response.json()["result"]["response"]

def call_github(model: str, prompt: str) -> str:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return "❌ GITHUB_TOKEN tidak diset. Daftar di https://github.com/"
    url = "https://models.inference.ai.azure.com/chat/completions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 4096}
    response = requests.post(url, headers=headers, json=data, timeout=120)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def call_huggingface(model: str, prompt: str) -> str:
    api_key = os.environ.get("HF_TOKEN")
    if not api_key:
        return "❌ HF_TOKEN tidak diset. Daftar di https://huggingface.co/"
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"inputs": prompt, "parameters": {"max_new_tokens": 4096, "temperature": 0.7}}
    response = requests.post(url, headers=headers, json=data, timeout=120)
    response.raise_for_status()
    result = response.json()
    if isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", "")
    elif isinstance(result, dict):
        return result.get("generated_text", "")
    return str(result)

def call_ovh(model: str, prompt: str) -> str:
    url = "https://api-inference.cloud.ovh.net/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 4096}
    response = requests.post(url, headers=headers, json=data, timeout=120)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def call_llm7(model: str, prompt: str) -> str:
    url = "https://api.llm7.ai/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 4096}
    response = requests.post(url, headers=headers, json=data, timeout=120)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def call_openai(model: str, prompt: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "❌ OPENAI_API_KEY tidak diset"
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 4096}
    response = requests.post(url, headers=headers, json=data, timeout=120)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def call_anthropic(model: str, prompt: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "❌ ANTHROPIC_API_KEY tidak diset"
    url = "https://api.anthropic.com/v1/messages"
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
    data = {"model": model, "max_tokens": 4096, "messages": [{"role": "user", "content": prompt}]}
    response = requests.post(url, headers=headers, json=data, timeout=120)
    response.raise_for_status()
    return response.json()["content"][0]["text"]

# ==================== ROUTER ====================

class Router:
    TASK_TO_AI = {
        "coding": ["openrouter-qwen", "openrouter-nemotron", "groq-llama", "gemini-flash", "nvidia-llama", "mistral-codestral", "claude"],
        "debugging": ["openrouter-qwen", "openrouter-nemotron", "groq-llama", "gemini-pro", "nvidia-llama", "mistral-codestral", "claude"],
        "architecture": ["openrouter-nemotron", "openrouter-qwen", "gemini-pro", "groq-llama", "nvidia-llama", "claude"],
        "writing": ["openrouter-llama", "groq-llama", "gemini-flash", "openai-mini"],
        "translation": ["openrouter-mistral", "groq-gemma", "gemini-flash"],
        "summarization": ["openrouter-mistral", "groq-gemma", "gemini-flash"],
        "research": ["openrouter-gpt-oss", "gemini-pro", "groq-llama", "nvidia-llama", "claude"],
        "data_analysis": ["openrouter-gpt-oss", "gemini-pro", "groq-llama", "nvidia-llama", "openai"],
        "general": ["openrouter-llama", "groq-llama", "gemini-flash", "openrouter-mistral"],
        "simple_qa": ["openrouter-mistral", "groq-gemma", "lokal-kecil", "openrouter-llama"],
        "creative": ["openrouter-llama", "groq-llama", "gemini-flash", "openai"],
    }
    
    @classmethod
    def select_best_ai(cls, task_types: List[Tuple[str, float]], prefer_free: bool = True) -> Tuple[str, float]:
        main_task = task_types[0][0] if task_types else "general"
        ai_list = cls.TASK_TO_AI.get(main_task, ["openrouter-llama", "groq-llama", "openai-mini"])
        if prefer_free:
            free_ais = [ai for ai in ai_list if is_free_model(ai)]
            if free_ais:
                selected = free_ais[0]
                return selected, AI_WORKERS.get(selected, {}).get("cost", 0)
        selected = ai_list[0]
        return selected, AI_WORKERS.get(selected, {}).get("cost", 0)
    
    @classmethod
    def get_all_ai_for_swarm(cls, task_types: List[Tuple[str, float]]) -> List[str]:
        main_task = task_types[0][0] if task_types else "general"
        ai_list = cls.TASK_TO_AI.get(main_task, ["openrouter-llama", "groq-llama", "openai-mini"])
        free_ais = [ai for ai in ai_list if is_free_model(ai)]
        paid_ais = [ai for ai in ai_list if not is_free_model(ai)]
        result = free_ais[:5] + paid_ais[:2]
        return result[:7]

# ==================== TASK CLASSIFIER ====================

class TaskClassifier:
    TASK_PATTERNS = {
        "coding": [r"\b(code|function|class|api|endpoint|python|javascript|go|rust|java)\b", r"```"],
        "debugging": [r"\b(debug|error|fix|bug|troubleshoot|issue|problem)\b"],
        "architecture": [r"\b(architecture|design|structure|pattern|refactor|system)\b"],
        "writing": [r"\b(write|draft|article|blog|essay|story|email|poem)\b"],
        "translation": [r"\b(translate|terjemah|alih bahasa|from|to|dari|ke)\b"],
        "summarization": [r"\b(summarize|ringkas|summary|rangkuman|brief)\b"],
        "research": [r"\b(research|study|analyze|investigate|explore|paper)\b"],
        "data_analysis": [r"\b(analyze|analysis|data|statistics|chart|graph|dataset)\b"],
        "creative": [r"\b(creative|imaginative|story|poem|song|brainstorm)\b"],
        "educational": [r"\b(explain|teach|learn|education|tutorial|guide)\b"],
        "general": [r"\b(help|assist|how to|what is|explain|tell me|bantu|tolong)\b"],
        "simple_qa": [r"^(what|who|where|when|why|how|is|are|do|does|apa|siapa|di mana|kapan|mengapa|bagaimana)", r"^.{0,50}$"],
    }
    
    @classmethod
    def classify(cls, prompt: str) -> List[Tuple[str, float]]:
        prompt_lower = prompt.lower()
        results = []
        for task_type, patterns in cls.TASK_PATTERNS.items():
            confidence = 0
            for pattern in patterns:
                if re.search(pattern, prompt_lower, re.IGNORECASE):
                    confidence += 0.3
                elif re.search(pattern, prompt, re.IGNORECASE):
                    confidence += 0.2
            if task_type == "simple_qa" and len(prompt) < 50:
                confidence += 0.2
            if confidence > 0:
                results.append((task_type, min(confidence, 1.0)))
        results.sort(key=lambda x: x[1], reverse=True)
        if not results:
            results.append(("general", 0.5))
        return results

# ==================== MODE FUNCTIONS ====================

def mode_single(ai: Optional[str], prompt: str, prefer_free: bool = True):
    print("\n" + "="*60)
    print("  🎯 MODE SINGLE")
    print("="*60)
    task_types = TaskClassifier.classify(prompt)
    print(f"  📋 Tugas: {task_types[0][0] if task_types else 'general'} ({task_types[0][1]:.0%})")
    if not ai:
        ai, cost = Router.select_best_ai(task_types, prefer_free)
    else:
        cost = AI_WORKERS.get(ai, {}).get("cost", 0)
    is_free = is_free_model(ai)
    print(f"  🤖 AI: {ai} {'🆓 GRATIS' if is_free else '💰 Berbayar'}")
    print(f"  📝 Prompt: {prompt[:100]}..." if len(prompt) > 100 else f"  📝 Prompt: {prompt}")
    print("")
    response, cost = call_ai(ai, prompt)
    print("─"*60)
    print(response)
    print("─"*60)
    print(f"\n💲 Cost: ${cost:.4f} {'🆓 GRATIS!' if is_free else ''}")

def mode_swarm(prompt: str, prefer_free: bool = True):
    print("\n" + "="*60)
    print("  🐝 MODE SWARM")
    print("="*60)
    task_types = TaskClassifier.classify(prompt)
    workers = Router.get_all_ai_for_swarm(task_types)
    free_count = sum(1 for w in workers if is_free_model(w))
    print(f"  🤖 AI: {len(workers)} model ({free_count} gratis)")
    print(f"  📝 Prompt: {prompt[:100]}..." if len(prompt) > 100 else f"  📝 Prompt: {prompt}")
    print("")
    results = {}
    with ThreadPoolExecutor(max_workers=min(len(workers), 6)) as executor:
        future_to_worker = {executor.submit(call_ai, worker, prompt): worker for worker in workers}
        for future in as_completed(future_to_worker):
            worker = future_to_worker[future]
            try:
                response, cost = future.result()
                results[worker] = {"response": response, "cost": cost}
            except Exception as e:
                results[worker] = {"response": f"❌ Error: {str(e)}", "cost": 0}
    print("─"*60)
    print("  📊 HASIL SEMUA AI")
    print("─"*60)
    all_responses = ""
    total_cost = 0
    for worker, data in results.items():
        is_free = is_free_model(worker)
        print(f"\n🤖 {worker} {'🆓' if is_free else '💰'} (${data['cost']:.4f})")
        print("─"*60)
        print(data['response'])
        all_responses += f"\n=== {worker} ===\n{data['response']}"
        total_cost += data['cost']
    print(f"\n💲 Total Cost: ${total_cost:.4f}")

def mode_orchestrate(prompt: str, max_iter: int = 3, prefer_free: bool = True):
    print("\n" + "="*60)
    print("  🎼 MODE ORCHESTRATE")
    print("="*60)
    task_types = TaskClassifier.classify(prompt)
    current_ai, _ = Router.select_best_ai(task_types, prefer_free)
    print(f"  📋 Tugas: {task_types[0][0] if task_types else 'general'}")
    print(f"  🤖 AI awal: {current_ai} {'🆓' if is_free_model(current_ai) else '💰'}")
    print(f"  📝 Prompt: {prompt[:100]}..." if len(prompt) > 100 else f"  📝 Prompt: {prompt}")
    print("")
    last_response = ""
    iteration = 1
    while iteration <= max_iter:
        print(f"\n{'─'*60}")
        print(f"  ITERASI {iteration}/{max_iter}")
        print(f"{'─'*60}")
        print(f"🧠 Eksekusi oleh {current_ai}...")
        response, cost = call_ai(current_ai, prompt)
        last_response = response
        print("\n" + "─"*60)
        print(response)
        print("─"*60)
        print(f"💲 Cost: ${cost:.4f}")
        score = verify_response(response, prompt)
        print(f"\n📊 Skor: {score}/4")
        if score >= 3:
            print("\n✅ JAWABAN LOLOS VERIFIKASI!")
            print("\n📝 FINAL ANSWER:")
            print("─"*60)
            print(last_response)
            print("─"*60)
            return
        if iteration >= max_iter:
            print("\n⚠️ Mencapai batas maksimal iterasi")
            print("\n📝 FINAL ANSWER:")
            print("─"*60)
            print(last_response)
            print("─"*60)
            return
        print("\n❌ Jawaban perlu perbaikan")
        rotation = ["openrouter-qwen", "groq-llama", "gemini-flash", "nvidia-llama", "openrouter-nemotron"]
        if current_ai in rotation:
            idx = rotation.index(current_ai)
            current_ai = rotation[(idx + 1) % len(rotation)]
        else:
            current_ai = rotation[0]
        print(f"🔄 AI berikutnya: {current_ai} {'🆓' if is_free_model(current_ai) else '💰'}")
        prompt = f"""Feedback: Perbaiki jawaban berikut.\n\nKONTEKS ASLI: {prompt}\n\nJAWABAN SEBELUMNYA:\n{last_response}\n\nJAWABAN BARU YANG LEBIH BAIK:"""
        iteration += 1

def verify_response(response: str, prompt: str) -> int:
    score = 0
    if len(response) > 100:
        score += 1
    if len(response) > 0:
        score += 1
    if "```" in response or any(syntax in response for syntax in ["def ", "class ", "function"]):
        score += 1
    keywords = " ".join(prompt.split()[:3])
    if any(keyword.lower() in response.lower() for keyword in keywords.split()):
        score += 1
    return min(score, 4)

# ==================== SHOW MODELS ====================

def show_models():
    print("\n" + "="*70)
    print("  🤖 NYX-ROUTER - Available Models")
    print("="*70)
    free_models = get_free_models()
    paid_models = get_paid_models()
    print(f"\n🆓 FREE MODELS ({len(free_models)}):")
    print("─"*70)
    providers = {}
    for model in free_models:
        config = AI_WORKERS[model]
        provider = config.get("provider", "unknown")
        if provider not in providers:
            providers[provider] = []
        providers[provider].append(model)
    for provider, models in providers.items():
        print(f"\n  📦 {provider.upper()} ({len(models)} models)")
        for model in models:
            config = AI_WORKERS[model]
            strength = ", ".join(config.get("strength", [])[:2])
            limit = config.get("limit", "Unlimited")
            print(f"    ✅ {model}")
            print(f"       💪 {strength}")
            print(f"       📊 {limit}")
    print(f"\n💎 PAID MODELS ({len(paid_models)}):")
    print("─"*70)
    for model in paid_models:
        config = AI_WORKERS[model]
        provider = config.get("provider", "unknown")
        cost = config.get("cost", 0)
        print(f"  💰 {model} ({provider}) - ${cost}/1M tokens")

def show_apis():
    print("\n" + "="*70)
    print("  🔑 FREE API KEYS - Cara Daftar")
    print("="*70)
    print("""
    1. OPENROUTER_API_KEY - https://openrouter.ai/
    2. GROQ_API_KEY - https://console.groq.com/
    3. GOOGLE_API_KEY - https://aistudio.google.com/
    4. NVIDIA_API_KEY - https://build.nvidia.com/
    5. CEREBRAS_API_KEY - https://cloud.cerebras.ai/
    6. MISTRAL_API_KEY - https://console.mistral.ai/
    7. CLOUDFLARE_API_KEY + CLOUDFLARE_ACCOUNT_ID - https://dash.cloudflare.com/
    8. GITHUB_TOKEN - https://github.com/
    9. HF_TOKEN - https://huggingface.co/
    
    SET API KEYS:
    export OPENROUTER_API_KEY="sk-or-..."
    export GROQ_API_KEY="gsk_..."
    export GOOGLE_API_KEY="AIza..."
    export NVIDIA_API_KEY="nvapi-..."
    export CEREBRAS_API_KEY="..."
    export MISTRAL_API_KEY="..."
    export CLOUDFLARE_API_KEY="..."
    export CLOUDFLARE_ACCOUNT_ID="..."
    export GITHUB_TOKEN="..."
    export HF_TOKEN="..."
    """)

# ==================== CLI ====================

def nyx_cli():
    import argparse
    parser = argparse.ArgumentParser(description="NYX-ROUTER v2.2.0")
    subparsers = parser.add_subparsers(dest="command")
    single_parser = subparsers.add_parser("single")
    single_parser.add_argument("prompt", nargs="*")
    single_parser.add_argument("--ai")
    single_parser.add_argument("--free", action="store_true", default=True)
    swarm_parser = subparsers.add_parser("swarm")
    swarm_parser.add_argument("prompt", nargs="*")
    swarm_parser.add_argument("--free", action="store_true", default=True)
    orch_parser = subparsers.add_parser("orch")
    orch_parser.add_argument("prompt", nargs="*")
    orch_parser.add_argument("--max", type=int, default=3)
    orch_parser.add_argument("--free", action="store_true", default=True)
    models_parser = subparsers.add_parser("models")
    apis_parser = subparsers.add_parser("apis")
    version_parser = subparsers.add_parser("version")
    
    args = parser.parse_args()
    
    if args.command == "single":
        prompt = " ".join(args.prompt)
        if prompt:
            mode_single(args.ai, prompt, args.free)
        else:
            print("❌ Prompt wajib diisi")
    elif args.command == "swarm":
        prompt = " ".join(args.prompt)
        if prompt:
            mode_swarm(prompt, args.free)
        else:
            print("❌ Prompt wajib diisi")
    elif args.command == "orch":
        prompt = " ".join(args.prompt)
        if prompt:
            mode_orchestrate(prompt, args.max, args.free)
        else:
            print("❌ Prompt wajib diisi")
    elif args.command == "models":
        show_models()
    elif args.command == "apis":
        show_apis()
    elif args.command == "version":
        print("🌙 NYX-ROUTER v2.2.0")
        print(f"   {len(AI_WORKERS)} models total")
        print(f"   {len(get_free_models())} free models")
        print("   Providers: 14 (11 free)")
        print("   License: MIT")
    else:
        parser.print_help()

if __name__ == "__main__":
    nyx_cli()
