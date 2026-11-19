#!/usr/bin/env python3
"""
AI Model Auto-Tracker & Notifier
- Fetches all active AI models & 100% Free models from global APIs
- Detects new models added since last check
- Sends Android push notification via Termux API
- Updates models_data.json and rebuilds index.html
- Pushes directly to GitHub
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
from datetime import datetime

REPO_DIR = "/data/user/0/com.termux/files/home/projects/ai-model-compass"
KNOWN_MODELS_FILE = os.path.join(REPO_DIR, "known_models.json")
MODELS_DATA_FILE = os.path.join(REPO_DIR, "models_data.json")

def notify_user(title, message):
    try:
        subprocess.run([
            "termux-notification",
            "-t", title,
            "-c", message,
            "--sound",
            "--priority", "high"
        ], check=False)
        print(f"📢 Notification sent: {title} - {message}")
    except Exception as e:
        print(f"⚠️ Notification error: {e}")

def fetch_openrouter_models():
    url = "https://openrouter.ai/api/v1/models"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("data", [])
    except Exception as e:
        print(f"Error fetching OpenRouter models: {e}")
        return []

def categorize_model(model_id, name, desc):
    text = f"{model_id} {name} {desc}".lower()
    categories = []
    
    if any(k in text for k in ["code", "coder", "coding", "dev", "program", "syntax"]):
        categories.append("code")
    if any(k in text for k in ["reason", "r1", "thought", "math", "logic", "thinking"]):
        categories.append("reasoning")
    if any(k in text for k in ["free", ":free"]):
        categories.append("free")
    if any(k in text for k in ["vision", "flash", "creative", "prose", "write", "chat"]):
        categories.append("creative")
        
    if not categories:
        categories.append("free" if ":free" in model_id else "creative")
        
    return " ".join(categories)

def run_tracker():
    os.chdir(REPO_DIR)
    models = fetch_openrouter_models()
    if not models:
        print("No models fetched, aborting.")
        return

    # Load known models
    known_ids = set()
    if os.path.exists(KNOWN_MODELS_FILE):
        try:
            with open(KNOWN_MODELS_FILE, "r") as f:
                known_ids = set(json.load(f))
        except Exception:
            known_ids = set()

    current_ids = set(m.get("id") for m in models)
    new_model_ids = current_ids - known_ids
    
    # Process structured models
    structured_models = []
    
    # 1. First add curated flagship models for guaranteed high quality
    curated_flagships = [
        {
            "id": "deepseek/deepseek-r1",
            "name": "DeepSeek R1",
            "tag": "King of Reasoning & Code",
            "badge": "Open-Weights / SOTA",
            "category": "code reasoning free",
            "desc": "OpenAI o1 और Claude Sonnet के बराबर रीजनिंग। गणित, कॉम्प्लेक्स बग्स और लॉजिक के लिए बेस्ट।",
            "free_url": "https://chat.deepseek.com",
            "free_where": "chat.deepseek.com ($0 Free Web)",
            "context_length": 64000,
            "is_free": True
        },
        {
            "id": "anthropic/claude-3.7-sonnet",
            "name": "Claude 3.7 Sonnet (Thinking)",
            "tag": "Best for Coding & Architecture",
            "badge": "Hybrid Reasoning",
            "category": "code creative reasoning",
            "desc": "विश्व का नंबर 1 कोडिंग मॉडल। क्लीन कोड, आर्किटेक्चर, UI डिजाइन और हाई-क्वालिटी कंटेंट में बेजोड़।",
            "free_url": "https://claude.ai",
            "free_where": "claude.ai (Free Tier Available)",
            "context_length": 200000,
            "is_free": False
        },
        {
            "id": "google/gemini-2.5-flash",
            "name": "Gemini 2.5 Flash",
            "tag": "1M+ Context & Superfast",
            "badge": "Generous Free API",
            "category": "free creative code",
            "desc": "बड़ी फाइल्स, पूरी बुक्स, और रोज़मर्रा के तेज़ सवालों के लिए 100% बेस्ट स्पीड और 1M टोकन मेमोरी।",
            "free_url": "https://aistudio.google.com",
            "free_where": "aistudio.google.com ($0 Free API)",
            "context_length": 1048576,
            "is_free": True
        },
        {
            "id": "qwen/qwen-2.5-coder-32b-instruct",
            "name": "Qwen 2.5 Coder 32B",
            "tag": "Top Open-Source Coder",
            "badge": "100% Free on Groq",
            "category": "code free",
            "desc": "Alibaba का शानदार मॉडल। Python, Web, C++ और ऑटोमेशन कोडिंग में क्लॉड को टक्कर देता है।",
            "free_url": "https://groq.com",
            "free_where": "Groq & OpenRouter ($0 Free API)",
            "context_length": 32768,
            "is_free": True
        }
    ]
    structured_models.extend(curated_flagships)

    # 2. Add dynamically tracked 100% Free models from API
    for m in models:
        m_id = m.get("id", "")
        pricing = m.get("pricing", {})
        p_in = float(pricing.get("prompt", 0) or 0)
        p_out = float(pricing.get("completion", 0) or 0)
        is_free = (p_in == 0 and p_out == 0) or ":free" in m_id

        if is_free and not any(x["id"] == m_id for x in structured_models):
            name = m.get("name") or m_id.split("/")[-1]
            desc = m.get("description", "") or "High performance open model available with $0 API charges."
            # Clean up desc
            if len(desc) > 160:
                desc = desc[:157] + "..."
            cat = categorize_model(m_id, name, desc)
            if "free" not in cat:
                cat += " free"

            structured_models.append({
                "id": m_id,
                "name": name,
                "tag": "100% Free Tier Model",
                "badge": "Free API",
                "category": cat,
                "desc": desc,
                "free_url": f"https://openrouter.ai/{m_id}",
                "free_where": "OpenRouter Free ($0)",
                "context_length": m.get("context_length", 32000),
                "is_free": True
            })

    # Save models_data.json
    with open(MODELS_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(structured_models, f, ensure_ascii=False, indent=2)

    # Update known models
    with open(KNOWN_MODELS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(current_ids), f, indent=2)

    print(f"✅ Processed {len(structured_models)} models ({len(new_model_ids)} newly discovered).")

    # If new models detected, notify user!
    if new_model_ids and len(known_ids) > 0:
        new_names = [m.get("name", m.get("id")) for m in models if m.get("id") in list(new_model_ids)[:3]]
        sample_str = ", ".join(new_names)
        notify_user("🧭 AI Model Tracker Alert!", f"नये मॉडल्स लॉन्च हुए: {sample_str} (कुल {len(new_model_ids)} नए)")

    # Rebuild HTML with dynamic hydration
    update_html(structured_models)

    # Git commit and push
    subprocess.run(["git", "add", "."], check=False)
    diff = subprocess.run(["git", "diff", "--staged", "--quiet"], check=False).returncode
    if diff != 0:
        subprocess.run(["git", "commit", "-m", f"Auto-track AI models update ({datetime.now().strftime('%Y-%m-%d %H:%M')})"], check=False)
        subprocess.run(["git", "push", "origin", "main"], check=False)
        print("🚀 Changes committed & pushed to GitHub!")

def update_html(models_data):
    # Generates dynamic cards inside index.html
    html_template = """<!DOCTYPE html>
<html lang="hi" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Model Compass | कौन सा AI मॉडल कब यूज़ करें?</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: '#3b82f6',
            cardbg: '#1e293b',
            darkbg: '#0f172a'
          }
        }
      }
    }
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', 'Noto Sans Devanagari', sans-serif; }
    .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen pb-16 antialiased selection:bg-blue-500 selection:text-white">

  <!-- Header -->
  <header class="sticky top-0 z-50 glass border-b border-slate-800 px-4 py-3 sm:py-4">
    <div class="max-w-4xl mx-auto flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <span class="text-2xl">🧭</span>
        <div>
          <h1 class="text-lg sm:text-xl font-bold bg-gradient-to-r from-blue-400 via-teal-300 to-indigo-400 bg-clip-text text-transparent">AI Model Compass</h1>
          <p class="text-xs text-slate-400 hidden sm:block">याद रखने की झंझट खत्म — जानिए कौन सा AI मॉडल किस काम के लिए बेस्ट है</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-[11px] bg-slate-800/80 border border-slate-700/60 text-slate-300 px-2 py-1 rounded-md hidden sm:inline-block">🟢 Auto-Tracked</span>
        <button onclick="shareLink()" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-sm transition active:scale-95">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/></svg>
          <span>Share Link</span>
        </button>
      </div>
    </div>
  </header>

  <main class="max-w-4xl mx-auto px-4 pt-6 space-y-6">

    <!-- Search & Filter -->
    <section class="space-y-3">
      <div class="relative">
        <input type="text" id="searchInput" oninput="filterModels()" placeholder="🔍 सर्च करें (जैसे: code, reasoning, free, deepseek, claude)..." 
          class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition">
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-medium">
        <button onclick="setCategory('all')" id="btn-all" class="filter-btn active py-2.5 px-3 rounded-xl border border-blue-500/50 bg-blue-500/20 text-blue-300 font-semibold flex items-center justify-center gap-1.5 transition">
          🔥 All Top Models
        </button>
        <button onclick="setCategory('code')" id="btn-code" class="filter-btn py-2.5 px-3 rounded-xl border border-slate-800 bg-slate-900 text-slate-300 hover:bg-slate-800 flex items-center justify-center gap-1.5 transition">
          💻 Coding & Dev
        </button>
        <button onclick="setCategory('reasoning')" id="btn-reasoning" class="filter-btn py-2.5 px-3 rounded-xl border border-slate-800 bg-slate-900 text-slate-300 hover:bg-slate-800 flex items-center justify-center gap-1.5 transition">
          🧠 Deep Logic & Math
        </button>
        <button onclick="setCategory('free')" id="btn-free" class="filter-btn py-2.5 px-3 rounded-xl border border-slate-800 bg-slate-900 text-slate-300 hover:bg-slate-800 flex items-center justify-center gap-1.5 transition">
          ⚡ 100% Free Tier ($0)
        </button>
      </div>
    </section>

    <!-- Golden Rule Box -->
    <div class="p-4 rounded-2xl bg-gradient-to-r from-blue-900/30 via-slate-900/40 to-purple-900/30 border border-blue-500/30 text-xs sm:text-sm text-slate-300 flex items-start gap-3">
      <span class="text-xl">💡</span>
      <div>
        <strong class="text-blue-300">याद रखने का सीधा नियम (Golden Rule):</strong><br>
        1. कोडिंग और लॉजिक के लिए 👉 <b>DeepSeek R1 / V3</b> और <b>Qwen 2.5 Coder</b> (100% Free & Best)।<br>
        2. कॉम्प्लेक्स ऐप्स और आर्किटेक्चर के लिए 👉 <b>Claude 3.7 Sonnet</b>।<br>
        3. बड़ी बुक्स, PDF और रोज़मर्रा के सवालों के लिए 👉 <b>Gemini 2.5 Flash</b> (1M Context)।
      </div>
    </div>

    <!-- Models Grid -->
    <section class="space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold uppercase tracking-wider text-slate-400">ट्रैक्ड मॉडल्स (Tracked AI Models)</h3>
        <span id="model-count" class="text-xs text-slate-400 font-medium"></span>
      </div>
      
      <div id="models-container" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Injected via JavaScript -->
      </div>
    </section>

    <!-- Free Hubs Section -->
    <section class="border border-slate-800 bg-slate-900/50 rounded-2xl p-5 space-y-4">
      <h3 class="text-sm font-bold text-white flex items-center gap-2">
        <span>🎁</span> मुफ्त में बड़े मॉडल्स कैसे चलाएं? (Free Hubs Guide)
      </h3>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
        <div class="p-3 bg-slate-800/60 rounded-xl border border-slate-700/50 space-y-1">
          <div class="font-bold text-blue-300">1. OpenRouter.ai</div>
          <p class="text-slate-400">फ़िल्टर में 'Free' सेलेक्ट करें। DeepSeek, Llama और Mistral के दर्जनों मॉडल्स $0 में मिलेंगे।</p>
        </div>
        <div class="p-3 bg-slate-800/60 rounded-xl border border-slate-700/50 space-y-1">
          <div class="font-bold text-teal-300">2. Google AI Studio</div>
          <p class="text-slate-400">Gemini 2.5 Pro और Flash की फ्री API की (Generous Free Quota) तुरंत मिलती है।</p>
        </div>
        <div class="p-3 bg-slate-800/60 rounded-xl border border-slate-700/50 space-y-1">
          <div class="font-bold text-purple-300">3. Groq Cloud</div>
          <p class="text-slate-400">सुपर-फास्ट स्पीड (500 tokens/sec)। Llama 3.3 और Qwen बिना किसी फीस के उपयोग करें।</p>
        </div>
      </div>
    </section>

  </main>

  <!-- Share Toast -->
  <div id="toast" class="fixed bottom-6 left-1/2 transform -translate-x-1/2 bg-blue-600 text-white text-xs px-4 py-2 rounded-full shadow-lg opacity-0 pointer-events-none transition duration-300">
    Link copied to clipboard! 📋
  </div>

  <script>
    const modelsData = """ + json.dumps(models_data, ensure_ascii=False) + """;
    let activeCategory = 'all';

    function renderModels() {
      const container = document.getElementById('models-container');
      const query = (document.getElementById('searchInput').value || '').toLowerCase();
      
      const filtered = modelsData.filter(m => {
        const matchesCategory = activeCategory === 'all' || (m.category && m.category.includes(activeCategory));
        const matchesSearch = !query || 
          m.name.toLowerCase().includes(query) || 
          m.id.toLowerCase().includes(query) || 
          (m.desc && m.desc.toLowerCase().includes(query)) ||
          (m.category && m.category.toLowerCase().includes(query));
        return matchesCategory && matchesSearch;
      });

      document.getElementById('model-count').innerText = `${filtered.length} Models`;

      if (filtered.length === 0) {
        container.innerHTML = `<div class="col-span-full py-12 text-center text-slate-500 text-sm">कोई मॉडल नहीं मिला। कृपया सर्च टर्म बदलें।</div>`;
        return;
      }

      container.innerHTML = filtered.map(m => `
        <div class="model-card border border-slate-800 bg-slate-900/90 rounded-2xl p-4 space-y-3 hover:border-slate-700 transition flex flex-col justify-between">
          <div class="space-y-2">
            <div class="flex items-start justify-between">
              <div>
                <div class="flex items-center gap-2">
                  <h4 class="font-bold text-base text-white">${m.name}</h4>
                  <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold ${m.is_free ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-purple-500/20 text-purple-400 border border-purple-500/30'}">${m.badge || (m.is_free ? 'Free' : 'Pro')}</span>
                </div>
                <p class="text-xs text-blue-400 font-medium mt-0.5">${m.tag || 'AI Model'}</p>
              </div>
              <span class="text-xl">${m.is_free ? '⚡' : '🧠'}</span>
            </div>
            <p class="text-xs text-slate-300 leading-relaxed">${m.desc || ''}</p>
          </div>
          
          <div class="pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
            <span class="text-slate-400">फ्री: <b class="text-slate-200">${m.free_where || 'OpenRouter'}</b></span>
            <a href="${m.free_url}" target="_blank" rel="noopener" class="text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1">Try &rarr;</a>
          </div>
        </div>
      `).join('');
    }

    function setCategory(cat) {
      activeCategory = cat;
      document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('border-blue-500/50', 'bg-blue-500/20', 'text-blue-300', 'font-semibold');
        btn.classList.add('border-slate-800', 'bg-slate-900', 'text-slate-300');
      });
      const activeBtn = document.getElementById(`btn-${cat}`);
      if (activeBtn) {
        activeBtn.classList.add('border-blue-500/50', 'bg-blue-500/20', 'text-blue-300', 'font-semibold');
        activeBtn.classList.remove('border-slate-800', 'bg-slate-900', 'text-slate-300');
      }
      renderModels();
    }

    function filterModels() {
      renderModels();
    }

    function shareLink() {
      if (navigator.share) {
        navigator.share({
          title: 'AI Model Compass',
          text: 'कौन सा AI मॉडल कब यूज़ करें? पूरी फ्री गाइड:',
          url: window.location.href
        }).catch(() => copyLink());
      } else {
        copyLink();
      }
    }

    function copyLink() {
      navigator.clipboard.writeText(window.location.href);
      const toast = document.getElementById('toast');
      toast.classList.remove('opacity-0');
      setTimeout(() => toast.classList.add('opacity-0'), 2000);
    }

    // Initial render
    renderModels();
  </script>
</body>
</html>
"""
    with open(os.path.join(REPO_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_template)
    print("✅ index.html updated successfully with dynamic search & filtering!")

if __name__ == "__main__":
    run_tracker()
