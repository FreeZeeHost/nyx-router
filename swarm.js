#!/usr/bin/env node
// ================================================================
//  NYX-ROUTER - Swarm Mode (Node.js)
//  Parallel execution with 47+ models
// ================================================================

const { exec } = require('child_process');

// ==================== AI WORKERS ====================
const AI_WORKERS = {
    'lokal-kecil': { type: 'ollama', model: 'llama3.2:3b', cost: 0 },
    'lokal-sedang': { type: 'ollama', model: 'qwen2.5-coder:7b', cost: 0 },
    'lokal-besar': { type: 'ollama', model: 'deepseek-coder:6.7b', cost: 0 },
    'openrouter-auto': { type: 'openrouter', model: 'openrouter/auto', cost: 0 },
    'openrouter-qwen': { type: 'openrouter', model: 'qwen/qwen-2.5-72b-instruct', cost: 0 },
    'openrouter-llama': { type: 'openrouter', model: 'meta-llama/llama-3.3-70b-instruct', cost: 0 },
    'openrouter-mistral': { type: 'openrouter', model: 'mistralai/mistral-7b-instruct', cost: 0 },
    'groq-llama': { type: 'groq', model: 'llama-3.3-70b-versatile', cost: 0 },
    'groq-gemma': { type: 'groq', model: 'gemma2-9b-it', cost: 0 },
    'groq-mixtral': { type: 'groq', model: 'mixtral-8x7b-32768', cost: 0 },
    'gemini-flash': { type: 'google', model: 'gemini-2.0-flash-exp', cost: 0 },
    'gemini-pro': { type: 'google', model: 'gemini-2.0-pro-exp', cost: 0 },
    'nvidia-llama': { type: 'nvidia', model: 'meta/llama-3.1-70b-instruct', cost: 0 },
    'nvidia-mistral': { type: 'nvidia', model: 'mistralai/mixtral-8x7b-instruct', cost: 0 },
    'openai-mini': { type: 'openai', model: 'gpt-4o-mini', cost: 0.15 },
    'openai': { type: 'openai', model: 'gpt-4o', cost: 5 },
    'claude': { type: 'anthropic', model: 'claude-3-5-sonnet-20241022', cost: 3 },
};

function callAI(worker, prompt) {
    return new Promise((resolve) => {
        const config = AI_WORKERS[worker];
        if (!config) {
            resolve({ worker, response: `❌ Worker '${worker}' tidak ditemukan`, cost: 0, success: false });
            return;
        }

        let cmd = '';
        if (config.type === 'ollama') {
            cmd = `ollama run ${config.model} "${prompt.replace(/"/g, '\\"')}"`;
        } else if (config.type === 'openrouter') {
            const apiKey = process.env.OPENROUTER_API_KEY;
            if (!apiKey) { resolve({ worker, response: '❌ OPENROUTER_API_KEY tidak diset', cost: 0, success: false }); return; }
            cmd = `curl -s https://openrouter.ai/api/v1/chat/completions -H "Authorization: Bearer ${apiKey}" -H "Content-Type: application/json" -d '{"model":"${config.model}","messages":[{"role":"user","content":"${prompt.replace(/'/g, "\\'").replace(/"/g, '\\"')}"}],"temperature":0.7,"max_tokens":4096}' | jq -r '.choices[0].message.content'`;
        } else if (config.type === 'groq') {
            const apiKey = process.env.GROQ_API_KEY;
            if (!apiKey) { resolve({ worker, response: '❌ GROQ_API_KEY tidak diset', cost: 0, success: false }); return; }
            cmd = `curl -s https://api.groq.com/openai/v1/chat/completions -H "Authorization: Bearer ${apiKey}" -H "Content-Type: application/json" -d '{"model":"${config.model}","messages":[{"role":"user","content":"${prompt.replace(/'/g, "\\'").replace(/"/g, '\\"')}"}],"temperature":0.7,"max_tokens":4096}' | jq -r '.choices[0].message.content'`;
        } else if (config.type === 'google') {
            const apiKey = process.env.GOOGLE_API_KEY;
            if (!apiKey) { resolve({ worker, response: '❌ GOOGLE_API_KEY tidak diset', cost: 0, success: false }); return; }
            cmd = `curl -s "https://generativelanguage.googleapis.com/v1beta/models/${config.model}:generateContent?key=${apiKey}" -H "Content-Type: application/json" -d '{"contents":[{"parts":[{"text":"${prompt.replace(/"/g, '\\"')}"}]}],"generationConfig":{"temperature":0.7,"maxOutputTokens":4096}}' | jq -r '.candidates[0].content.parts[0].text'`;
        } else if (config.type === 'nvidia') {
            const apiKey = process.env.NVIDIA_API_KEY;
            if (!apiKey) { resolve({ worker, response: '❌ NVIDIA_API_KEY tidak diset', cost: 0, success: false }); return; }
            cmd = `curl -s https://integrate.api.nvidia.com/v1/chat/completions -H "Authorization: Bearer ${apiKey}" -H "Content-Type: application/json" -d '{"model":"${config.model}","messages":[{"role":"user","content":"${prompt.replace(/'/g, "\\'").replace(/"/g, '\\"')}"}],"temperature":0.7,"max_tokens":4096}' | jq -r '.choices[0].message.content'`;
        } else if (config.type === 'openai') {
            const apiKey = process.env.OPENAI_API_KEY;
            if (!apiKey) { resolve({ worker, response: '❌ OPENAI_API_KEY tidak diset', cost: 0, success: false }); return; }
            cmd = `curl -s https://api.openai.com/v1/chat/completions -H "Authorization: Bearer ${apiKey}" -H "Content-Type: application/json" -d '{"model":"${config.model}","messages":[{"role":"user","content":"${prompt.replace(/'/g, "\\'").replace(/"/g, '\\"')}"}],"temperature":0.7,"max_tokens":4096}' | jq -r '.choices[0].message.content'`;
        } else if (config.type === 'anthropic') {
            const apiKey = process.env.ANTHROPIC_API_KEY;
            if (!apiKey) { resolve({ worker, response: '❌ ANTHROPIC_API_KEY tidak diset', cost: 0, success: false }); return; }
            cmd = `curl -s https://api.anthropic.com/v1/messages -H "x-api-key: ${apiKey}" -H "anthropic-version: 2023-06-01" -H "Content-Type: application/json" -d '{"model":"${config.model}","max_tokens":4096,"messages":[{"role":"user","content":"${prompt.replace(/'/g, "\\'").replace(/"/g, '\\"')}"}]}' | jq -r '.content[0].text'`;
        } else {
            resolve({ worker, response: `❌ Tipe '${config.type}' tidak dikenal`, cost: 0, success: false });
            return;
        }

        exec(cmd, { timeout: 120000 }, (error, stdout, stderr) => {
            if (error) {
                resolve({ worker, response: `❌ Error: ${error.message}`, cost: 0, success: false });
            } else if (stderr) {
                resolve({ worker, response: `❌ Stderr: ${stderr}`, cost: 0, success: false });
            } else {
                const response = stdout.trim() || '❌ Tidak ada response';
                resolve({ worker, response, cost: config.cost, success: true });
            }
        });
    });
}

async function modeSwarm(prompt) {
    console.log('\n' + '='.repeat(60));
    console.log('  🐝 NYX-SWARM v2.2');
    console.log('='.repeat(60));
    
    const allWorkers = Object.keys(AI_WORKERS);
    const freeWorkers = allWorkers.filter(w => AI_WORKERS[w].cost === 0);
    const selected = freeWorkers.slice(0, 6);
    
    console.log(`  🤖 AI: ${selected.join(', ')}`);
    console.log(`  📝 Prompt: ${prompt.length > 100 ? prompt.slice(0, 100) + '...' : prompt}`);
    console.log('');
    
    console.log('⏳ Menjalankan semua AI secara paralel...\n');
    const promises = selected.map(worker => callAI(worker, prompt));
    const results = await Promise.all(promises);
    
    console.log('─'.repeat(60));
    console.log('  📊 HASIL SEMUA AI');
    console.log('─'.repeat(60));
    
    let allResponses = '';
    let totalCost = 0;
    let successful = 0;
    
    for (const result of results) {
        const isFree = result.cost === 0;
        console.log(`\n🤖 ${result.worker} ${isFree ? '🆓' : '💰'} ($${result.cost.toFixed(4)})`);
        console.log('─'.repeat(60));
        console.log(result.response);
        console.log('');
        if (result.success) successful++;
        allResponses += `\n=== ${result.worker} ===\n${result.response}`;
        totalCost += result.cost;
    }
    console.log(`✅ ${successful}/${results.length} berhasil`);
    console.log(`💲 Total Cost: $${totalCost.toFixed(4)}`);
}

const prompt = process.argv.slice(2).join(' ');
if (!prompt) {
    console.log('Usage: node swarm.js "prompt"');
    process.exit(1);
}
modeSwarm(prompt).catch(console.error);
