import sqlite3
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "..", "data", "incidents.db")


def save_incident(scene, risk):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS incidents(
            id INTEGER PRIMARY KEY,
            scene TEXT,
            risk REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("INSERT INTO incidents(scene, risk) VALUES (?,?)", (scene, risk))
    con.commit()
    iid = cur.lastrowid
    con.close()
    return iid


def fetch_incidents():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM incidents ORDER BY id DESC")
    data = cur.fetchall()
    con.close()
    return data
