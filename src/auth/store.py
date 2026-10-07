"""Local account store (SQLite). Tables isolate auth so Postgres can replace this file later."""

import hashlib
import json
import os
import secrets
import sqlite3
import time

DB_ENV = "AUTH_DB_PATH"
SESSION_DAYS = 30


def db_path() -> str:
    p = os.getenv(DB_ENV, "data/users.db")
    if not os.path.isabs(p):
        base = os.path.dirname(os.path.abspath(__file__))
        p = os.path.normpath(os.path.join(base, "..", "..", p))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def _db() -> sqlite3.Connection:
    con = sqlite3.connect(db_path())
    con.row_factory = sqlite3.Row
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
      salt TEXT NOT NULL, hash TEXT NOT NULL, created REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS sessions(
      token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL, expires REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS progress(
      user_id INTEGER PRIMARY KEY, data TEXT NOT NULL DEFAULT '{}');
    """)
    return con


def _hash(pw: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 200_000).hex()


def register(name: str, email: str, password: str) -> tuple:
    name, email = (name or "").strip(), (email or "").strip().lower()
    if not name or not email or "@" not in email:
        return None, "Enter a valid name and email."
    if not password or len(password) < 8:
        return None, "Password needs at least 8 characters."
    salt = secrets.token_hex(16)
    con = _db()
    try:
        cur = con.execute("INSERT INTO users(name,email,salt,hash,created) VALUES(?,?,?,?,?)",
                          (name, email, salt, _hash(password, salt), time.time()))
        con.commit()
        return {"id": cur.lastrowid, "name": name, "email": email}, ""
    except sqlite3.IntegrityError:
        return None, "That email is already registered — log in instead."
    finally:
        con.close()


def verify(email: str, password: str) -> tuple:
    con = _db()
    try:
        r = con.execute("SELECT * FROM users WHERE email=?", ((email or "").strip().lower(),)).fetchone()
    finally:
        con.close()
    if not r or _hash(password or "", r["salt"]) != r["hash"]:
        return None, "Wrong email or password."
    return {"id": r["id"], "name": r["name"], "email": r["email"]}, ""


def new_session(user_id: int) -> str:
    tok = secrets.token_hex(32)
    th = hashlib.sha256(tok.encode()).hexdigest()
    con = _db()
    try:
        con.execute("INSERT INTO sessions(token_hash,user_id,expires) VALUES(?,?,?)",
                    (th, user_id, time.time() + SESSION_DAYS * 86400))
        con.commit()
    finally:
        con.close()
    return tok


def check_session(tok: str):
    if not tok:
        return None
    th = hashlib.sha256(tok.encode()).hexdigest()
    con = _db()
    try:
        r = con.execute("SELECT s.expires,u.id,u.name,u.email FROM sessions s JOIN users u ON u.id=s.user_id "
                        "WHERE s.token_hash=?", (th,)).fetchone()
    finally:
        con.close()
    if not r or r["expires"] < time.time():
        return None
    return {"id": r["id"], "name": r["name"], "email": r["email"]}


def end_session(tok: str) -> None:
    if not tok:
        return
    con = _db()
    try:
        con.execute("DELETE FROM sessions WHERE token_hash=?", (hashlib.sha256(tok.encode()).hexdigest(),))
        con.commit()
    finally:
        con.close()


def load_progress(user_id: int) -> dict:
    con = _db()
    try:
        r = con.execute("SELECT data FROM progress WHERE user_id=?", (user_id,)).fetchone()
        return json.loads(r["data"]) if r else {}
    except Exception:
        return {}
    finally:
        con.close()


def save_progress(user_id: int, data: dict) -> None:
    con = _db()
    try:
        con.execute("INSERT INTO progress(user_id,data) VALUES(?,?) "
                    "ON CONFLICT(user_id) DO UPDATE SET data=excluded.data",
                    (user_id, json.dumps(data)))
        con.commit()
    except Exception:
        pass
    finally:
        con.close()
