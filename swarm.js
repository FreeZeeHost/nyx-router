#!/usr/bin/env node
const { exec } = require('child_process');
const AI_WORKERS = {
    'lokal-kecil': { type: 'ollama', model: 'llama3.2:3b', cost: 0 },
    'lokal-sedang': { type: 'ollama', model: 'qwen2.5-coder:7b', cost: 0 },
    'openrouter-auto': { type: 'openrouter', model: 'openrouter/auto', cost: 0 },
    'openrouter-qwen': { type: 'openrouter', model: 'qwen/qwen-2.5-72b-instruct', cost: 0 },
    'groq-llama': { type: 'groq', model: 'llama-3.3-70b-versatile', cost: 0 },
    'gemini-flash': { type: 'google', model: 'gemini-2.0-flash-exp', cost: 0 },
    'openai-mini': { type: 'openai', model: 'gpt-4o-mini', cost: 0.15 },
    'openai': { type: 'openai', model: 'gpt-4o', cost: 5 },
    'claude': { type: 'anthropic', model: 'claude-3-5-sonnet-20241022', cost: 3 },
};

function callAI(worker, prompt) {
    return new Promise((resolve) => {
        const config = AI_WORKERS[worker];
        if (!config) { resolve({ worker, response: '❌ Worker tidak ditemukan', cost: 0 }); return; }
        let cmd = `ollama run ${config.model} "${prompt}"`;
        exec(cmd, { timeout: 120000 }, (error, stdout) => {
            if (error) resolve({ worker, response: '❌ Error', cost: 0 });
            else resolve({ worker, response: stdout.trim(), cost: config.cost });
        });
    });
}

async function modeSwarm(prompt) {
    console.log('\n🐝 NYX-SWARM');
    const workers = Object.keys(AI_WORKERS).slice(0, 6);
    console.log('🤖 AI:', workers.join(', '));
    const results = await Promise.all(workers.map(w => callAI(w, prompt)));
    results.forEach(r => console.log(`\n${r.worker}:\n${r.response}`));
}

const prompt = process.argv.slice(2).join(' ');
if (!prompt) { console.log('Usage: node swarm.js "prompt"'); process.exit(1); }
modeSwarm(prompt);
