import sqlite3
import json

def save_to_db(uid, interested_subjects, learning_preference, evaluation):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        uid Integer PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS user_profiles(
        uid Integer PRIMARY KEY,
        interested_subjects TEXT,
        learning_preference TEXT NOT NULL,
        evaluation_of_user_json TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE
        )""")
    
    cursor.execute("""
                   INSERT OR IGNORE INTO users (uid, email, password_hash)
                   VALUES (?, ?, ?)""", (uid,f"user_{uid}@example.com", "dummy_hash"))

    cursor.execute('''
        INSERT OR REPLACE INTO user_profiles (uid, interested_subjects, learning_preference, evaluation_of_user_json,updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (uid, interested_subjects, learning_preference, json.dumps(evaluation)))
    
    conn.commit()
    conn.close()
    
def fetch_userdata(uid:int):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT interested_subjects, learning_preference, evaluation_of_user_json
                   FROM user_profiles
                   WHERE uid = ?
                   """, (uid,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "interested_subjects": row[0],
            "learning_preference": row[1],
            "evaluation_of_user": json.loads(row[2])
        }
    else:
        return None