"""
WATRANA RAG System - Flask Web Application
==========================================
Run: python app.py
Then open: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import sqlite3

# Import RAG engine functions
from rag_engine import ask_question, rebuild_index, translate_answer

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "watrana-secret-2024")


@app.route("/")
def index():
    """Main chatbot page"""
    return render_template("index.html")


@app.route("/api/ask", methods=["POST"])
def api_ask():
    """
    RAG Query API
    Body: {"question": "...", "language": "english|hindi|hinglish"}
    """
    data = request.get_json()

    if not data or "question" not in data:
        return jsonify({"error": "Question is missing"}), 400

    question = data["question"].strip()
    language = data.get("language", "english").strip().lower()

    if not question:
        return jsonify({"error": "Question must not be empty"}), 400

    if len(question) > 1000:
        return jsonify({"error": "Question is too long. Maximum allowed length is 1000 characters"}), 400

    result = ask_question(question, language)
    return jsonify(result)


@app.route("/api/translate", methods=["POST"])
def api_translate():
    """
    Translate already generated answer.
    Body: {"answer": "...", "language": "english|hindi|hinglish"}
    """
    data = request.get_json()

    if not data or "answer" not in data:
        return jsonify({"error": "Answer is missing"}), 400

    answer = data["answer"].strip()
    language = data.get("language", "english").strip().lower()

    if not answer:
        return jsonify({"error": "Answer must not be empty"}), 400

    result = translate_answer(answer, language)
    return jsonify(result)


@app.route("/api/stats", methods=["GET"])
def api_stats():
    """Database statistics API"""
    try:
        conn = sqlite3.connect("data/watrana.db")
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM problems")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT category, COUNT(*) FROM problems GROUP BY category ORDER BY COUNT(*) DESC")
        categories = [{"name": row[0], "count": row[1]} for row in cursor.fetchall()]

        cursor.execute("SELECT MIN(year), MAX(year) FROM problems")
        year_range = cursor.fetchone()

        cursor.execute("SELECT department, COUNT(*) FROM problems GROUP BY department ORDER BY COUNT(*) DESC")
        departments = [{"name": row[0], "count": row[1]} for row in cursor.fetchall()]

        cursor.execute("SELECT SUM(downtime_hours) FROM problems")
        total_downtime = cursor.fetchone()[0] or 0

        conn.close()

        return jsonify({
            "total_problems": total,
            "categories": categories,
            "year_range": {"from": year_range[0], "to": year_range[1]},
            "departments": departments,
            "total_downtime_hours": total_downtime
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/rebuild", methods=["POST"])
def api_rebuild():
    """Vector store rebuild API"""
    try:
        result = rebuild_index()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/history", methods=["GET"])
def api_history():
    """All problems list API"""
    try:
        category = request.args.get("category", "")
        department = request.args.get("department", "")

        conn = sqlite3.connect("data/watrana.db")
        cursor = conn.cursor()

        query = "SELECT id, year, category, problem, solution, downtime_hours, department FROM problems WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)
        if department:
            query += " AND department = ?"
            params.append(department)

        query += " ORDER BY year DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        problems = []
        for row in rows:
            problems.append({
                "id": row[0],
                "year": row[1],
                "category": row[2],
                "problem": row[3],
                "solution": row[4],
                "downtime_hours": row[5],
                "department": row[6]
            })

        return jsonify({"problems": problems})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    if not os.path.exists("data/watrana.db"):
        print("⚠️  Database not found! Please run: python create_database.py")

    print("✅ Using local Ollama LLM. No OpenAI API key required.")
    print("\n🚀 WATRANA RAG Server is starting...")
    print("🌐 Open this URL in your browser: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server\n")

    app.run(
        debug=os.getenv("FLASK_DEBUG", "True") == "True",
        host="0.0.0.0",
        port=5000
    )