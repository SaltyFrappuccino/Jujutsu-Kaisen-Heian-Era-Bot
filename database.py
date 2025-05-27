import sqlite3
import json
from config import PENDING_TEXT_CURSED_TECHNIQUE, PENDING_TEXT_EQUIPMENT

DB_NAME = 'rp_bot.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        with open('db_schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.commit()

def set_user_state(vk_id, state, data=None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO user_states (vk_id, state, data) VALUES (?, ?, ?)",
            (vk_id, state, json.dumps(data) if data else None)
        )
        conn.commit()

def get_user_state(vk_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT state, data FROM user_states WHERE vk_id = ?", (vk_id,))
        row = cursor.fetchone()
        if row:
            return row['state'], json.loads(row['data']) if row['data'] else None
        return None, None

def clear_user_state(vk_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_states WHERE vk_id = ?", (vk_id,))
        conn.commit()

def add_character(char_data):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        columns = ', '.join(char_data.keys())
        placeholders = ', '.join('?' * len(char_data))
        sql = f"INSERT INTO characters ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, tuple(char_data.values()))
        conn.commit()
        return cursor.lastrowid

def get_character_by_owner_id(owner_vk_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM characters WHERE owner_vk_id = ?", (owner_vk_id,))
        return cursor.fetchone()

def get_character_by_id(char_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM characters WHERE id = ?", (char_id,))
        return cursor.fetchone()

def get_all_characters():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, owner_vk_id, full_name FROM characters ORDER BY full_name")
        return cursor.fetchall()

def update_character_field(char_id, field, value):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        sql = f"UPDATE characters SET {field} = ? WHERE id = ?"
        cursor.execute(sql, (value, char_id))
        conn.commit()

def update_character_multiple_fields(char_id, updates_dict):
    if not updates_dict:
        return
    with get_db_connection() as conn:
        cursor = conn.cursor()
        set_clauses = []
        values = []
        for field, value in updates_dict.items():
            set_clauses.append(f"{field} = ?")
            values.append(value)
        values.append(char_id)
        sql = f"UPDATE characters SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(sql, tuple(values))
        conn.commit()


def start_pending_text(vk_id, text_type, target_char_id=None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO pending_text (vk_id, text_type, content, target_char_id) VALUES (?, ?, ?, ?)",
            (vk_id, text_type, "", target_char_id)
        )
        conn.commit()

def append_pending_text(vk_id, text_chunk):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM pending_text WHERE vk_id = ?", (vk_id,))
        row = cursor.fetchone()
        if row:
            new_content = row['content'] + "\n" + text_chunk if row['content'] else text_chunk
            cursor.execute("UPDATE pending_text SET content = ? WHERE vk_id = ?", (new_content, vk_id))
            conn.commit()

def get_pending_text_info(vk_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT text_type, content, target_char_id FROM pending_text WHERE vk_id = ?", (vk_id,))
        return cursor.fetchone()

def clear_pending_text(vk_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pending_text WHERE vk_id = ?", (vk_id,))
        conn.commit()

init_db()