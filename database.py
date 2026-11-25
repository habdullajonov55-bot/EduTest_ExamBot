import sqlite3
import json
from pathlib import Path

DB_PATH = Path("data/testbot.sqlite3")

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grade INTEGER NOT NULL,
            subject TEXT NOT NULL,
            card INTEGER NOT NULL CHECK(card BETWEEN 1 AND 4),
            qtype TEXT NOT NULL CHECK(qtype IN ('fan','iq')),
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            correct INTEGER NOT NULL CHECK(correct BETWEEN 0 AND 3),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        con.execute("""
        CREATE TABLE IF NOT EXISTS students (
            telegram_id INTEGER PRIMARY KEY,
            school TEXT NOT NULL,
            grade INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

def save_student(telegram_id, school, grade, full_name):
    with connect() as con:
        con.execute("""
        INSERT INTO students(telegram_id, school, grade, full_name)
        VALUES(?,?,?,?)
        ON CONFLICT(telegram_id) DO UPDATE SET
        school=excluded.school, grade=excluded.grade,
        full_name=excluded.full_name, updated_at=CURRENT_TIMESTAMP
        """, (telegram_id, school, grade, full_name))

def add_question(grade, subject, card, qtype, question, options, correct):
    with connect() as con:
        con.execute("""
        INSERT INTO questions(grade, subject, card, qtype, question, options, correct)
        VALUES(?,?,?,?,?,?,?)
        """, (grade, subject, card, qtype, question,
              json.dumps(options, ensure_ascii=False), correct))

def eligible_cards(grade, subject):
    with connect() as con:
        rows = con.execute("""
        SELECT card,
          SUM(CASE WHEN qtype='fan' THEN 1 ELSE 0 END) AS fan_count,
          SUM(CASE WHEN qtype='iq' THEN 1 ELSE 0 END) AS iq_count
        FROM questions
        WHERE grade=? AND subject=?
        GROUP BY card
        """, (grade, subject)).fetchall()
    return [r["card"] for r in rows if r["fan_count"] >= 18 and r["iq_count"] >= 7]

def get_test_questions(grade, subject, card):
    import random
    with connect() as con:
        fan = con.execute("""
        SELECT * FROM questions WHERE grade=? AND subject=? AND card=? AND qtype='fan'
        """, (grade, subject, card)).fetchall()
        iq = con.execute("""
        SELECT * FROM questions WHERE grade=? AND subject=? AND card=? AND qtype='iq'
        """, (grade, subject, card)).fetchall()
    fan = random.sample(list(fan), 18)
    iq = random.sample(list(iq), 7)
    result = []
    for row in fan:
        item = dict(row)
        item["options"] = json.loads(item["options"])
        result.append(item)
    for row in iq:
        item = dict(row)
        item["options"] = json.loads(item["options"])
        result.append(item)
    random.shuffle(result)
    return result

def question_stats():
    with connect() as con:
        total = con.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        grades = con.execute("SELECT COUNT(DISTINCT grade) FROM questions").fetchone()[0]
        cards = con.execute("SELECT COUNT(DISTINCT card) FROM questions").fetchone()[0]
    return total, grades, cards
