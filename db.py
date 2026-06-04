import sqlite3
import json
from datetime import datetime
import streamlit as st

@st.cache_resource
def init_db():
    conn = sqlite3.connect('professors.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS professor_papers(
            author_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            papers_json TEXT NOT NULL,
            time TEXT
        )
    """)
    return conn

def save_papers(conn, author, papers):
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO professor_papers (author_id, name, papers_json, time) VALUES (?, ?, ?, ?)",
            (author['authorId'], author['name'], json.dumps(papers), datetime.now().isoformat())
        )

def get_papers_cache(conn, author_id):
    row = conn.execute("SELECT papers_json FROM professor_papers WHERE author_id = ?", (author_id,)).fetchone()
    return json.loads(row["papers_json"]) if row else None