#!/usr/bin/env python3
"""
Master AI Model Tracker & Categorizer with Date-wise Sorting (Latest on Top)
- Tracks ALL models with launch/release dates
- Sorts by Release Date (Latest First)
- Automatically adds new models dynamically from OpenRouter & Global APIs
- Updates both GitHub README.md and Live Website index.html
"""

import os
import sys
import json
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
    except Exception as e:
        print(f"Notification error: {e}")

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

def build_database(api_models):
    api_map = {m.get("id"): m for m in api_models}

    # Core curated models with explicit accurate release dates & metadata
    curated = [
        {
            "id": "anthropic/claude-3.7-sonnet",
            "name": "Claude 3.7 Sonnet (Hybrid Thinking)",
            "provider": "anthropic",
            "provider_name": "Anthropic",
            "release_date": "2025-02-24",
            "tag": "World #1 Coding & Hybrid Thinking",
            "badge": "Hybrid Thinking",
            "categories": ["all", "claude", "code", "reasoning", "creative"],
            "desc": "हाइब्रिड रीजनिंग के साथ दुनिया का नंबर 1 कोडिंग मॉडल। रिएक्ट ऐप्स, फुल-स्टैक डेवलपमेंट और क्लीन आर्किटेक्चर में बेजोड़।",
            "best_for": "फुल-स्टैक कोडिंग, यूआई डिजाइन, मुश्किल कोड आर्किटेक्चर",
            "free_where": "claude.ai (Free Daily Messages)",
            "url": "https://claude.ai",
            "is_free": True
        },
        {
            "id": "deepseek/deepseek-r1",
            "name": "DeepSeek R1",
            "provider": "deepseek",
            "provider_name": "DeepSeek",
            "release_date": "2025-01-20",
            "tag": "Open-Weights Reasoning King",
            "badge": "100% Free / Open",
            "categories": ["all", "deepseek", "reasoning", "code", "free"],
            "desc": "OpenAI o1 को टक्कर देने वाला ओपन-सोर्स रीजनिंग मॉडल। पूरा थिंकिंग प्रोसेस स्क्रीन पर दिखाता है।",
            "best_for": "कठिन गणित, साइंस, कॉम्प्लेक्स एल्गोरिदम",
            "free_where": "chat.deepseek.com ($0 Free Web)",
            "url": "https://chat.deepseek.com",
            "is_free": True
        },
        {
            "id": "deepseek/deepseek-chat",
            "name": "DeepSeek V3",
            "provider": "deepseek",
            "provider_name": "DeepSeek",
            "release_date": "2024-12-26",
            "tag": "671B General & Coding Powerhouse",
            "badge": "Ultra Low Cost / Free",
            "categories": ["all", "deepseek", "code", "daily", "free"],
            "desc": "671B पैरामीटर्स का विशाल मॉडल। GPT-4o स्तर की क्षमता $0 वेब चैट में मुफ़्त उपलब्ध।",
            "best_for": "बड़ी कोडिंग, आर्टिकल्स, डेली चैट",
            "free_where": "chat.deepseek.com ($0 Free)",
            "url": "https://chat.deepseek.com",
            "is_free": True
        },
        {
            "id": "google/gemini-2.5-pro",
            "name": "Google Gemini 2.5 Pro",
            "provider": "google",
            "provider_name": "Google",
            "release_date": "2025-02-15",
            "tag": "2 Million Huge Context King",
            "badge": "2M Huge Memory",
            "categories": ["all", "gemini", "reasoning", "creative"],
            "desc": "20 लाख टोकन्स की मेमोरी! पूरी किताबें, 1 घंटे के वीडियो और पूरी कोड रिपॉजिटरी एक साथ समझ लेता है।",
            "best_for": "बड़ी फाइल्स, लंबी PDFs, पूरी प्रोजेक्ट रिपॉजिटरी",
            "free_where": "aistudio.google.com ($0 Free Quota)",
            "url": "https://aistudio.google.com",
            "is_free": True
        },
        {
            "id": "google/gemini-2.5-flash",
            "name": "Google Gemini 2.5 Flash",
            "provider": "google",
            "provider_name": "Google",
            "release_date": "2025-02-10",
            "tag": "Sub-Second Ultra Fast (1M Memory)",
            "badge": "Free 1M Context",
            "categories": ["all", "gemini", "free", "daily", "code"],
            "desc": "बिजली जैसी तेज़ स्पीड और 10 लाख टोकन्स मेमोरी। Google AI Studio में भारी मात्रा में फ्री API उपलब्ध।",
            "best_for": "लाइव चैट, कोडिंग हेल्प, क्विक समरी",
            "free_where": "aistudio.google.com ($0 Free API)",
            "url": "https://aistudio.google.com",
            "is_free": True
        },
        {
            "id": "google/gemini-1.5-flash-thinking",
            "name": "Gemini 2.5 Flash Thinking",
            "provider": "google",
            "provider_name": "Google",
            "release_date": "2024-12-19",
            "tag": "Google's Free Reasoning Model",
            "badge": "Thinking / Free",
            "categories": ["all", "gemini", "reasoning", "free", "code"],
            "desc": "गूगल का फ्री रीजनिंग मॉडल जो जवाब देने से पहले खुद स्टेप-बाय-स्टेप सोचता है।",
            "best_for": "लॉजिक पहेलियाँ, कोड डिबगिंग, मैथ",
            "free_where": "aistudio.google.com ($0 Free)",
            "url": "https://aistudio.google.com",
            "is_free": True
        },
        {
            "id": "openai/o1",
            "name": "OpenAI o1 / o3-mini",
            "provider": "openai",
            "provider_name": "OpenAI",
            "release_date": "2025-01-31",
            "tag": "Advanced Thinking & Math",
            "badge": "Reasoning Model",
            "categories": ["all", "chatgpt", "reasoning", "code"],
            "desc": "सोच-समझकर जवाब देने वाला OpenAI का रीजनिंग मॉडल। मुश्किल मैथ और कॉम्पिटिटिव कोडिंग के लिए।",
            "best_for": "गहन विचार, Math, कॉम्पिटिटिव कोडिंग",
            "free_where": "chatgpt.com (Free Tier में o3-mini)",
            "url": "https://chatgpt.com",
            "is_free": True
        },
        {
            "id": "openai/gpt-4o",
            "name": "ChatGPT GPT-4o (Omni)",
            "provider": "openai",
            "provider_name": "OpenAI",
            "release_date": "2024-05-13",
            "tag": "All-Rounder Daily King",
            "badge": "Multimodal / Voice",
            "categories": ["all", "chatgpt", "creative", "daily"],
            "desc": "दैनिक चैटिंग, वॉयस बातचीत और फोटो देखकर समझाने के लिए सबसे लोकप्रिय ऑल-राउंडर AI।",
            "best_for": "दैनिक बातचीत, इमेज एनालिसिस, जनरल राइटिंग",
            "free_where": "chatgpt.com (Free Tier)",
            "url": "https://chatgpt.com",
            "is_free": True
        },
        {
            "id": "openai/gpt-4o-mini",
            "name": "GPT-4o Mini",
            "provider": "openai",
            "provider_name": "OpenAI",
            "release_date": "2024-07-18",
            "tag": "Superfast & Lightweight",
            "badge": "High Speed",
            "categories": ["all", "chatgpt", "free", "daily"],
            "desc": "सुपर-फास्ट और बहुत लाइटवेट। छोटे टास्क, समरी और ट्रांसलेशन के लिए बेस्ट।",
            "best_for": "फास्ट रिप्लाई, ट्रांसलेशन, क्विक ड्राफ्ट्स",
            "free_where": "chatgpt.com ($0 Free)",
            "url": "https://chatgpt.com",
            "is_free": True
        },
        {
            "id": "meta-llama/llama-3.3-70b-instruct",
            "name": "Meta Llama 3.3 (70B)",
            "provider": "meta",
            "provider_name": "Meta Llama",
            "release_date": "2024-12-06",
            "tag": "Open-Source Benchmark Leader",
            "badge": "Open Weights",
            "categories": ["all", "meta", "free", "daily", "code"],
            "desc": "मेटा का सबसे पावरफुल 70B मॉडल। Groq पर 500+ tokens/sec की गति से फ्री चलता है।",
            "best_for": "प्राइवेट AI, लोकल रनिंग, ओपन-सोर्स ऐप्स",
            "free_where": "groq.com & OpenRouter ($0 Free)",
            "url": "https://groq.com",
            "is_free": True
        },
        {
            "id": "qwen/qwen-2.5-coder-32b-instruct",
            "name": "Qwen 2.5 Coder (32B)",
            "provider": "qwen",
            "provider_name": "Alibaba Qwen",
            "release_date": "2024-11-12",
            "tag": "Dedicated Open-Source Coder",
            "badge": "Code Specialized",
            "categories": ["all", "qwen", "code", "free"],
            "desc": "Alibaba का विशेष कोडिंग मॉडल। 92+ प्रोग्रामिंग भाषाओं में क्लॉड/GPT को टक्कर देता है।",
            "best_for": "Python, JavaScript, Shell, Bug Fixing",
            "free_where": "groq.com & OpenRouter ($0 Free)",
            "url": "https://openrouter.ai",
            "is_free": True
        }
    ]

    # Dynamically ingest and parse newly discovered models from API
    for m in api_models:
        m_id = m.get("id", "")
        # Only take official clean models, skip batch/internal
        if ":batch" in m_id or "preview" in m_id and len(m_id) > 40:
            continue
            
        pricing = m.get("pricing", {})
        p_in = float(pricing.get("prompt", 0) or 0)
        p_out = float(pricing.get("completion", 0) or 0)
        is_free_api = (p_in == 0 and p_out == 0) or ":free" in m_id

        if is_free_api and not any(x["id"] == m_id for x in curated):
            created_ts = m.get("created")
            if created_ts:
                try:
                    rel_date = datetime.fromtimestamp(created_ts).strftime("%Y-%m-%d")
                except Exception:
                    rel_date = "2025-01-01"
            else:
                rel_date = "2025-01-01"

            name = m.get("name") or m_id.split("/")[-1]
            desc = m.get("description", "") or "High quality AI model accessible via free tier API."
            if len(desc) > 140:
                desc = desc[:137] + "..."

            provider = "other"
            if "google" in m_id: provider = "google"
            elif "openai" in m_id: provider = "openai"
            elif "meta" in m_id: provider = "meta"
            elif "qwen" in m_id: provider = "qwen"
            elif "deepseek" in m_id: provider = "deepseek"
            elif "anthropic" in m_id: provider = "anthropic"

            curated.append({
                "id": m_id,
                "name": name,
                "provider": provider,
                "provider_name": provider.capitalize(),
                "release_date": rel_date,
                "tag": "100% Free Tier Model",
                "badge": "Free API",
                "categories": ["all", "free", provider],
                "desc": desc,
                "best_for": "फ्री ऑटोमेशन और कोडिंग एक्सपेरिमेंट्स",
                "free_where": "OpenRouter ($0 API)",
                "url": f"https://openrouter.ai/{m_id}",
                "is_free": True
            })

    # SORT DATE-WISE: LATEST MODELS FIRST (Descending)
    curated.sort(key=lambda x: x.get("release_date", "2020-01-01"), reverse=True)
    return curated

def generate_readme(models):
    now_str = datetime.now().strftime("%d %B %Y")
    lines = [
        "# 🧭 AI Model Compass (Date-Wise Master Guide)",
        "",
        f"> ⚡ **Latest AI Models on Top (Updated: {now_str})**",
        "> याद रखने की झंझट खत्म! यहाँ दुनिया के सभी प्रमुख AI मॉडल्स लॉन्च डेट के अनुसार ऊपर से नीचे लिस्टेड हैं।",
        "",
        "---",
        "",
        "## 📅 Date-Wise AI Models Tracker (नया मॉडल सबसे ऊपर)",
        "",
        "| तारीख (Date) | AI मॉडल | कंपनी | किस काम के लिए बेस्ट है? | फ्री कहाँ मिलेगा? |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]

    for m in models:
        rel_date = m.get("release_date", "Latest")
        name = m.get("name", "")
        p_name = m.get("provider_name", "")
        best_for = m.get("best_for", m.get("tag", ""))
        free_where = m.get("free_where", "")
        url = m.get("url", "#")
        lines.append(f"| **{rel_date}** | [{name}]({url}) | {p_name} | {best_for} | [{free_where}]({url}) |")

    lines.extend([
        "",
        "---",
        "",
        "## 💡 1-नज़र में याद रखने का सीधा फॉर्मूला (Golden Rule)",
        "",
        "- 💻 **Coding, Debugging & Apps**: **Claude 3.7 Sonnet** (Top) / **DeepSeek V3** & **Qwen 2.5 Coder** (Free)",
        "- 🧠 **Deep Logic, Math & Thinking**: **DeepSeek R1** (Free) / **OpenAI o1**",
        "- 📚 **बड़ी फाइल्स, PDF, वीडियो (2M Tokens)**: **Google Gemini 2.5 Pro / Flash**",
        "- ⚡ **फास्ट डेली चैट & राइटिंग ($0)**: **ChatGPT GPT-4o Mini** / **Meta Llama 3.3**",
        "",
        "---",
        "",
        "## 🎁 $0 खर्च किए बिना AI चलाने के 3 सीक्रेट हब्स",
        "",
        "1. **Google AI Studio ([aistudio.google.com](https://aistudio.google.com))**: Gemini 2.5 Pro और Flash की फ्री API की तुरंत मिलती है। कोई क्रेडिट कार्ड नहीं चाहिए।",
        "2. **DeepSeek Official Web ([chat.deepseek.com](https://chat.deepseek.com))**: R1 (Reasoning) और V3 दोनों 100% मुफ़्त बिना किसी सब्सक्रिप्शन के चलते हैं।",
        "3. **Groq Cloud ([groq.com](https://groq.com))**: 500+ tokens/sec की गति से Llama 3.3 और Qwen बिना किसी फीस के इस्तेमाल करें।",
        "",
        "---",
        "",
        "## 🌐 लाइव इंटरएक्टिव वेब डैशबोर्ड",
        "अपने फोन में या दोस्तों को शेयर करने के लिए लाइव ऐप खोलें:",
        "👉 **[https://satyenderparihar.github.io/ai-model-compass/](https://satyenderparihar.github.io/ai-model-compass/)**"
    ])

    return "\n".join(lines)

def update_html(master_models):
    html_template = """<!DOCTYPE html>
<html lang="hi" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Model Compass | Date-Wise Latest AI Models</title>
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
    .glass { background: rgba(15, 23, 42, 0.88); backdrop-filter: blur(12px); }
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen pb-16 antialiased selection:bg-blue-500 selection:text-white">

  <!-- Header -->
  <header class="sticky top-0 z-50 glass border-b border-slate-800 px-4 py-3 sm:py-4">
    <div class="max-w-5xl mx-auto flex items-center justify-between">
      <div class="flex items-center space-x-2.5">
        <span class="text-2xl sm:text-3xl">🧭</span>
        <div>
          <h1 class="text-lg sm:text-xl font-bold bg-gradient-to-r from-blue-400 via-teal-300 to-indigo-400 bg-clip-text text-transparent">AI Model Compass</h1>
          <p class="text-[11px] text-slate-400 hidden sm:block">तारीख के अनुसार — लेटेस्ट AI मॉडल हमेशा सबसे ऊपर</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-[11px] bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-2.5 py-1 rounded-full font-medium">📅 Date-Sorted (Latest)</span>
        <button onclick="shareLink()" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow transition active:scale-95">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/></svg>
          <span>Share</span>
        </button>
      </div>
    </div>
  </header>

  <main class="max-w-5xl mx-auto px-4 pt-6 space-y-6">

    <!-- Search Input -->
    <div class="relative">
      <input type="text" id="searchInput" oninput="renderModels()" placeholder="🔍 सर्च करें (जैसे: ChatGPT, Gemini, Claude, DeepSeek, Coding, Free, 2025)..." 
        class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition shadow-inner">
    </div>

    <!-- Category Filter Tabs: By Brand & By Purpose -->
    <div class="space-y-3">
      <!-- Row 1: Brand Filters -->
      <div>
        <div class="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5">ब्रांड के अनुसार (By Provider)</div>
        <div class="flex items-center gap-1.5 overflow-x-auto no-scrollbar pb-1 text-xs">
          <button onclick="setFilter('all')" id="btn-all" class="cat-btn active whitespace-nowrap px-3 py-1.5 rounded-lg border border-blue-500/50 bg-blue-500/20 text-blue-300 font-semibold transition">
            🌟 All (Latest First)
          </button>
          <button onclick="setFilter('chatgpt')" id="btn-chatgpt" class="cat-btn whitespace-nowrap px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-300 hover:bg-slate-800 transition">
            🟢 ChatGPT (OpenAI)
          </button>
          <button onclick="setFilter('gemini')" id="btn-gemini" class="cat-btn whitespace-nowrap px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-300 hover:bg-slate-800 transition">
            🔵 Google Gemini
          </button>
          <button onclick="setFilter('claude')" id="btn-claude" class="cat-btn whitespace-nowrap px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-300 hover:bg-slate-800 transition">
            🟣 Claude (Anthropic)
          </button>
          <button onclick="setFilter('deepseek')" id="btn-deepseek" class="cat-btn whitespace-nowrap px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-300 hover:bg-slate-800 transition">
            ⚡ DeepSeek
          </button>
          <button onclick="setFilter('meta')" id="btn-meta" class="cat-btn whitespace-nowrap px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-300 hover:bg-slate-800 transition">
            🦙 Meta Llama
          </button>
          <button onclick="setFilter('qwen')" id="btn-qwen" class="cat-btn whitespace-nowrap px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-300 hover:bg-slate-800 transition">
            💻 Qwen Coder
          </button>
        </div>
      </div>

      <!-- Row 2: Purpose Filters -->
      <div>
        <div class="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5">ज़रूरत के अनुसार (By Purpose)</div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-medium">
          <button onclick="setFilter('code')" id="btn-code" class="cat-btn py-2 px-3 rounded-xl border border-slate-800 bg-slate-900 text-slate-300 hover:bg-slate-800 flex items-center justify-center gap-1.5 transition">
            💻 Coding & Dev
          </button>
          <button onclick="setFilter('reasoning')" id="btn-reasoning" class="cat-btn py-2 px-3 rounded-xl border border-slate-800 bg-slate-900 text-slate-300 hover:bg-slate-800 flex items-center justify-center gap-1.5 transition">
            🧠 Deep Logic & Math
          </button>
          <button onclick="setFilter('free')" id="btn-free" class="cat-btn py-2 px-3 rounded-xl border border-slate-800 bg-slate-900 text-slate-300 hover:bg-slate-800 flex items-center justify-center gap-1.5 transition">
            ⚡ 100% Free Tier ($0)
          </button>
          <button onclick="setFilter('daily')" id="btn-daily" class="cat-btn py-2 px-3 rounded-xl border border-slate-800 bg-slate-900 text-slate-300 hover:bg-slate-800 flex items-center justify-center gap-1.5 transition">
            💬 Daily Fast Chat
          </button>
        </div>
      </div>
    </div>

    <!-- Models List Header -->
    <div class="flex items-center justify-between pt-2">
      <div class="flex items-center gap-2">
        <h3 class="text-sm font-semibold uppercase tracking-wider text-slate-400">📅 डेट-वाइज़ मॉडल्स (Latest First)</h3>
      </div>
      <span id="model-count" class="text-xs text-slate-400 font-medium"></span>
    </div>

    <!-- Dynamic Cards Grid -->
    <div id="models-container" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- JavaScript will inject cards here -->
    </div>

    <!-- Free Access Hubs Guide -->
    <section class="border border-slate-800 bg-slate-900/50 rounded-2xl p-5 space-y-3">
      <h3 class="text-sm font-bold text-white flex items-center gap-2">
        <span>🎁</span> $0 खर्च किए बिना सबसे बड़े मॉडल्स कैसे चलाएं?
      </h3>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
        <div class="p-3 bg-slate-800/60 rounded-xl border border-slate-700/50 space-y-1">
          <div class="font-bold text-blue-300">1. Google AI Studio</div>
          <p class="text-slate-400">Gemini 2.5 Flash व Pro की फ्री API Key तुरंत मिलती है। कोई क्रेडिट कार्ड नहीं चाहिए।</p>
        </div>
        <div class="p-3 bg-slate-800/60 rounded-xl border border-slate-700/50 space-y-1">
          <div class="font-bold text-emerald-300">2. DeepSeek Web</div>
          <p class="text-slate-400">chat.deepseek.com पर R1 और V3 बिल्कुल 100% मुफ़्त में फुल पावर के साथ चलते हैं।</p>
        </div>
        <div class="p-3 bg-slate-800/60 rounded-xl border border-slate-700/50 space-y-1">
          <div class="font-bold text-purple-300">3. Groq Cloud</div>
          <p class="text-slate-400">Llama 3.3 और Qwen Coder को 500+ tokens/sec की सुपरफास्ट स्पीड पर $0 में चलाएं।</p>
        </div>
      </div>
    </section>

  </main>

  <!-- Share Toast Notification -->
  <div id="toast" class="fixed bottom-6 left-1/2 transform -translate-x-1/2 bg-blue-600 text-white text-xs px-4 py-2 rounded-full shadow-lg opacity-0 pointer-events-none transition duration-300 z-50">
    Link copied to clipboard! 📋
  </div>

  <script>
    const modelsData = """ + json.dumps(master_models, ensure_ascii=False) + """;
    let activeFilter = 'all';

    function renderModels() {
      const container = document.getElementById('models-container');
      const query = (document.getElementById('searchInput').value || '').toLowerCase().trim();

      const filtered = modelsData.filter(m => {
        const matchesFilter = activeFilter === 'all' || 
          (m.categories && m.categories.includes(activeFilter)) ||
          m.provider === activeFilter;

        const matchesQuery = !query || 
          m.name.toLowerCase().includes(query) || 
          m.id.toLowerCase().includes(query) || 
          (m.release_date && m.release_date.includes(query)) ||
          (m.desc && m.desc.toLowerCase().includes(query)) ||
          (m.provider_name && m.provider_name.toLowerCase().includes(query)) ||
          (m.best_for && m.best_for.toLowerCase().includes(query));

        return matchesFilter && matchesQuery;
      });

      document.getElementById('model-count').innerText = `${filtered.length} Models (Latest on Top)`;

      if (filtered.length === 0) {
        container.innerHTML = `
          <div class="col-span-full py-12 text-center text-slate-500 text-sm">
            कोई मॉडल नहीं मिला। कृपया दूसरा फ़िल्टर चुनें या सर्च बदलें।
          </div>`;
        return;
      }

      container.innerHTML = filtered.map(m => {
        let providerBadgeClass = 'bg-slate-700/50 text-slate-300 border-slate-600/50';
        if (m.provider === 'openai') providerBadgeClass = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
        else if (m.provider === 'google') providerBadgeClass = 'bg-blue-500/10 text-blue-400 border-blue-500/30';
        else if (m.provider === 'anthropic') providerBadgeClass = 'bg-purple-500/10 text-purple-400 border-purple-500/30';
        else if (m.provider === 'deepseek') providerBadgeClass = 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
        else if (m.provider === 'meta') providerBadgeClass = 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30';
        else if (m.provider === 'qwen') providerBadgeClass = 'bg-amber-500/10 text-amber-400 border-amber-500/30';

        return `
          <div class="border border-slate-800 bg-slate-900/90 rounded-2xl p-4 space-y-3 hover:border-slate-700 transition flex flex-col justify-between shadow-sm relative overflow-hidden">
            <div class="space-y-2">
              <div class="flex items-start justify-between gap-2">
                <div>
                  <div class="flex items-center gap-2 flex-wrap">
                    <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-900/40 text-blue-300 border border-blue-700/40">
                      📅 ${m.release_date || 'Latest'}
                    </span>
                    <h4 class="font-bold text-base text-white">${m.name}</h4>
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold border ${providerBadgeClass}">
                      ${m.provider_name}
                    </span>
                  </div>
                  <p class="text-xs text-blue-400 font-medium mt-1">${m.tag}</p>
                </div>
              </div>

              <p class="text-xs text-slate-300 leading-relaxed">${m.desc}</p>

              ${m.best_for ? `
                <div class="text-[11px] text-slate-400 bg-slate-950/60 p-2 rounded-lg border border-slate-800/80">
                  <span class="text-amber-400 font-semibold">🎯 सबसे बेस्ट:</span> ${m.best_for}
                </div>
              ` : ''}
            </div>

            <div class="pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
              <span class="text-slate-400">फ्री: <b class="text-slate-200">${m.free_where}</b></span>
              <a href="${m.url}" target="_blank" rel="noopener" class="text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1 active:scale-95 transition">
                Open &rarr;
              </a>
            </div>
          </div>
        `;
      }).join('');
    }

    function setFilter(filterKey) {
      activeFilter = filterKey;
      document.querySelectorAll('.cat-btn').forEach(btn => {
        btn.classList.remove('border-blue-500/50', 'bg-blue-500/20', 'text-blue-300', 'font-semibold');
        btn.classList.add('border-slate-800', 'bg-slate-900', 'text-slate-300');
      });
      const activeBtn = document.getElementById(`btn-${filterKey}`);
      if (activeBtn) {
        activeBtn.classList.add('border-blue-500/50', 'bg-blue-500/20', 'text-blue-300', 'font-semibold');
        activeBtn.classList.remove('border-slate-800', 'bg-slate-900', 'text-slate-300');
      }
      renderModels();
    }

    function shareLink() {
      if (navigator.share) {
        navigator.share({
          title: 'AI Model Compass',
          text: 'ChatGPT, Gemini, Claude, DeepSeek — कौन सा AI मॉडल कब यूज़ करें? डेट-वाइज़ पूरी गाइड:',
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
    print("✅ index.html generated with date-wise sorting (latest on top)!")

def main():
    os.chdir(REPO_DIR)
    api_models = fetch_openrouter_models()
    master_models = build_database(api_models)

    # 1. Update models_data.json
    with open(MODELS_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(master_models, f, ensure_ascii=False, indent=2)

    # 2. Update README.md with date-wise table
    readme_content = generate_readme(master_models)
    with open(os.path.join(REPO_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    # 3. Update index.html
    update_html(master_models)

    # 4. Commit and push to GitHub
    subprocess.run(["git", "add", "."], check=False)
    diff = subprocess.run(["git", "diff", "--staged", "--quiet"], check=False).returncode
    if diff != 0:
        subprocess.run(["git", "commit", "-m", f"Sort models by date (latest first) and update README table ({datetime.now().strftime('%Y-%m-%d %H:%M')})"], check=False)
        subprocess.run(["git", "push", "origin", "main"], check=False)
        print("🚀 Successfully pushed date-wise updates to GitHub!")

if __name__ == "__main__":
    main()
