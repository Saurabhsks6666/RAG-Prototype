markdown
# 🏭 WATRANA RAG System — Complete Beginner Guide (ENGLISH)

## What does this project do?

**RAG** (Retrieval-Augmented Generation) is an AI system that:
1. **Stores your own data** (20 years of problems) in a special database
2. When someone asks a question — **finds most similar past problems**  
3. Uses **ChatGPT** to generate **smart answers** based on those problems

User → Question → [RAG System] → Find Similar Problems → GPT Answer → User ↑ SQLite Database (20 years of data)


---

## 🗂️ Project Files Explained

watrana-rag/ │ ├── 📄 create_database.py → Creates SQLite database + sample data ├── 📄 rag_engine.py → Core RAG logic (embeddings, search, GPT) ├── 📄 app.py → Web server (Flask) - browser access ├── 📄 requirements.txt → Required libraries list ├── 📄 .env.example → API keys template ├── 📄 .env → Your actual API keys (create this file) │ ├── 📁 data/ │ ├── watrana.db → SQLite database (created by create_database.py) │ └── chroma_db/ → Vector embeddings store (created automatically) │ └── 📁 templates/ └── index.html → Web UI (shown in browser)


---

## 🛠️ Tools & Technologies — What they do & why used

Tool
	

What it does
	

Where to get

Python
	

Programming language
	

python.org

SQLite
	

Local database (file-based, no server needed)
	

Built into Python

OpenAI API
	

Embeddings + GPT answers
	

platform.openai.com

ChromaDB
	

Vector database (finds similar text)
	

pip install

LangChain
	

RAG framework (connects everything)
	

pip install

Flask
	

Web server (browser interface)
	

pip install

VS Code
	

Code editor
	

code.visualstudio.com
📋 STEP-BY-STEP SETUP GUIDE
─── STEP 1: Install Python ─────────────────────────────────────

Check if Python is installed:

bash
python --version

If not installed:

    Go to: https://www.python.org/downloads/
    Download Python 3.10 or 3.11 (green button)
    Install — "Add Python to PATH" checkbox MUST be checked!
    Restart VS Code

─── STEP 2: Install VS Code ────────────────────────────────────

    Go to: https://code.visualstudio.com/
    Download for your OS
    Install
    Install Extensions (VS Code left sidebar → 4 squares icon):
        Python (by Microsoft) — REQUIRED
        Pylance — Helpful

─── STEP 3: Open Project in VS Code ───────────────────────────

    Open VS Code
    File → Open Folder
    Select watrana-rag folder
    Full project will appear in VS Code

─── STEP 4: Open Terminal ──────────────────────────────────────

In VS Code:

    Press Ctrl + ` (backtick)
    Or Terminal → New Terminal from menu

Black terminal window opens — run commands here.
─── STEP 5: Create Virtual Environment ────────────────────────

Virtual environment creates isolated Python setup — libraries don't install globally.

bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

✅ Success sign: (venv) appears at start of terminal line
─── STEP 6: Install Libraries ──────────────────────────────────

bash
pip install -r requirements.txt

⏳ Takes 2-5 minutes. All libraries will download.
─── STEP 7: OpenAI Account & API Key ───────────────────────────

How to get OpenAI API KEY:

    Go to: https://platform.openai.com/signup
    Sign Up (email or Google)
    Verify email
    Login
    Left menu → API Keys
    "+ Create new secret key" button
    Name it (e.g., "Watrana RAG")
    Copy the key — shown only once, take screenshot!
        Looks like: sk-proj-abc123xyz...

💰 Cost details:

    New account gets $5 free credits
    Cost per question: ~$0.002 (2 cents)
    1000 questions = ~$2

Add payment method:

    Platform.openai.com → Billing
    Add credit card
    Set usage limit ($10-20 for safety)

─── STEP 8: Create .env File ───────────────────────────────────

    Copy .env.example file
    Rename to: .env (just dot-env, no extension)
    Open it and paste your API key:

OPENAI_API_KEY=sk-proj-your-actual-key-here
FLASK_SECRET_KEY=watrana-secret-2024
FLASK_DEBUG=True

⚠️ Important: Never share .env file on GitHub! It's secret.
─── STEP 9: Create Database ────────────────────────────────────

bash
python create_database.py

Expected output:

✅ Database created successfully!
✅ 20 sample records inserted!
📁 Database saved at: data/watrana.db

─── STEP 10: Start Server ──────────────────────────────────────

bash
python app.py

Expected output:

🚀 WATRANA RAG Server starting...
🌐 Open in browser: http://localhost:5000
⏹️  Stop server: Ctrl+C

─── STEP 11: Open in Browser ───────────────────────────────────

    Open browser (Chrome/Firefox)
    Type in address bar: http://localhost:5000
    Watrana RAG interface appears!

─── STEP 12: Test First Query ─────────────────────────────────

First query takes 30-60 seconds because:

    OpenAI generates embeddings
    ChromaDB saves them

After this, all queries are fast!

Type: "What is the solution for motor overheating problem?"
🔄 Adding Your Real Data
Option A: Add to SQLite directly

Open create_database.py and add your data to SAMPLE_DATA list:

python
{
    "year": 2024,
    "category": "Mechanical",  # Mechanical/Electrical/Hydraulic/Quality/Safety/Automation
    "problem": "Write actual problem here",
    "cause": "Write root cause here", 
    "solution": "Write solution here",
    "downtime_hours": 6,
    "department": "Production"
},

Then run:

bash
python create_database.py

Option B: Use GUI Database Editor

    Download: https://sqlitebrowser.org/
    Install
    Open data/watrana.db
    "Browse Data" tab → "problems" table
    Add/edit records using GUI
    Save changes

After adding new data — Rebuild Index!

In browser:

    Click "Index Rebuild" button (sidebar)
    Or restart: python app.py

❌ Common Problems & Solutions
Problem: ModuleNotFoundError

Cause: Libraries not installed
Solution:
  1. Check (venv) is active
  2. Run: pip install -r requirements.txt

Problem: OpenAI API Key invalid

Cause: .env file incorrect
Solution:
  1. Open .env file
  2. Check OPENAI_API_KEY (must start with sk-)
  3. No spaces before/after key

Problem: Database not found

Cause: create_database.py not run
Solution: Run python create_database.py first

Problem: Port 5000 already in use

Cause: Another program using port 5000
Solution: Change port=5001 in app.py

Problem: First query very slow

Cause: OpenAI embeddings generation (normal)
Solution: Wait — only first time, then fast

📱 WhatsApp Integration (Phase 2)

Once RAG system is ready, add WhatsApp:
Option A: Twilio (Recommended for beginners)

    Account: https://www.twilio.com/
    Activate WhatsApp Sandbox (free trial)
    pip install twilio
    Expose /api/ask using ngrok
    Set webhook in Twilio dashboard

Option B: Meta Cloud API (Official, Free)

    Account: https://developers.facebook.com/
    WhatsApp Business API setup
    More complex — test RAG first

ngrok (expose local server to internet):

bash
# Install: https://ngrok.com/download
ngrok http 5000
# Gives public URL like: https://abc123.ngrok.io
# Use this in WhatsApp webhook

💡 Project Architecture Summary

User types question
        ↓
Flask Web Server (app.py)
        ↓
RAG Engine (rag_engine.py)
        ↓
OpenAI Embeddings
(convert question to numbers)
        ↓
ChromaDB Vector Search
(find similar past problems)
        ↓
Select top 4 similar problems
        ↓
ChatGPT (gpt-3.5-turbo)
(generate answer based on problems)
        ↓
Answer → Show to user

🎯 Training Summary for New Team Members

3 key concepts to understand:

    Embeddings = Convert text to numbers (for comparison)
    Vector Search = Find similar numbers = Find similar problems
    RAG = Retrieve (find) + Augment (add context) + Generate (create answer)

What each file does:

    create_database.py → Data setup (run once)
    rag_engine.py → AI logic (don't modify normally)
    app.py → Web server (start this)
    .env → Secret keys (never share)

Made for Watrana — 20 Years of Industrial Knowledge
