"""
Database layer for Linktree Clone using SQLite3.
Provides thread-safe connections and helper CRUD functions.
"""
import sqlite3
import os
import json
import hashlib
import secrets
from typing import List, Dict, Any, Optional

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "linktree.db")

def get_connection() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"{salt}:{key.hex()}"

def verify_password(stored_hash: str, password: str) -> bool:
    try:
        if not stored_hash or ":" not in stored_hash:
            return False
        salt, key_hex = stored_hash.split(":", 1)
        computed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return secrets.compare_digest(computed.hex(), key_hex)
    except Exception:
        return False

def init_db():
    conn = get_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS profile (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL DEFAULT 'Aldian Dev',
                handle TEXT NOT NULL DEFAULT 'aldiandev',
                bio TEXT DEFAULT 'Full-Stack Developer, Content Creator & Tech Enthusiast 🚀',
                avatar_url TEXT DEFAULT '',
                avatar_size INTEGER DEFAULT 104,
                theme TEXT DEFAULT 'bps-pastel',
                socials TEXT DEFAULT '{}',
                footer_text TEXT DEFAULT '© 2026 Aldian. Built with Python & Tornado',
                show_share_button INTEGER DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                subtitle TEXT DEFAULT '',
                icon TEXT DEFAULT '🔗',
                category TEXT DEFAULT '',
                is_active INTEGER DEFAULT 1,
                is_highlighted INTEGER DEFAULT 0,
                sort_order INTEGER DEFAULT 0,
                click_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS click_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link_id INTEGER NOT NULL,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_agent TEXT,
                ip_address TEXT,
                FOREIGN KEY (link_id) REFERENCES links (id) ON DELETE CASCADE
            )
        """)

        # Migration: Check if avatar_size column exists in profile table
        cols = [row[1] for row in conn.execute("PRAGMA table_info(profile)").fetchall()]
        if "avatar_size" not in cols:
            conn.execute("ALTER TABLE profile ADD COLUMN avatar_size INTEGER DEFAULT 104")

        # Check default user
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS cnt FROM users")
        if cur.fetchone()["cnt"] == 0:
            default_pass_hash = hash_password("admin123")
            conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("admin", default_pass_hash))

        # Check default profile
        cur.execute("SELECT COUNT(*) AS cnt FROM profile WHERE id = 1")
        if cur.fetchone()["cnt"] == 0:
            default_socials = json.dumps({
                "whatsapp": "6281234567890",
                "instagram": "aldiandev",
                "facebook": "aldiandev",
                "github": "aldian",
                "linkedin": "aldiandev",
                "youtube": "@aldiandev",
                "tiktok": "",
                "twitter": "aldiandev",
                "email": "contact@aldian.dev",
                "website": "https://aldian.dev"
            })
            conn.execute("""
                INSERT INTO profile (id, name, handle, bio, avatar_url, theme, socials, footer_text, show_share_button)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                "Muhammad Aldian",
                "aldiandev",
                "Full-Stack Developer & Tech Explorer 🚀 | Sharing tips, projects, and guides.",
                "",
                "bps-pastel",
                default_socials,
                "© 2026 Aldian • Link in Bio"
            ))

        # Check default links
        cur.execute("SELECT COUNT(*) AS cnt FROM links")
        if cur.fetchone()["cnt"] == 0:
            sample_links = [
                ("Kunjungi Portal Website Resmi", "https://aldian.dev", "Portal informasi dan layanan resmi", "/static/icons/website.svg", "Utama", 1, 1, 0, 185),
                ("Portal Data Statistik Resmi (BPS)", "https://bps.go.id", "Akses publikasi, indikator, dan tabel statistik", "/static/icons/bps.svg", "Data & Publikasi", 1, 1, 1, 230),
                ("Official Channel YouTube", "https://youtube.com", "Tonton video tutorial, webinar & rilis data", "/static/icons/youtube.svg", "Media Sosial", 1, 0, 2, 142),
                ("Follow Instagram Kami", "https://instagram.com", "Info grafis harian dan kegiatan terbaru", "/static/icons/instagram.svg", "Media Sosial", 1, 0, 3, 118),
                ("Ikuti Update Terkini di X (Twitter)", "https://x.com", "Berita kilat dan diskusi publik", "/static/icons/x.svg", "Media Sosial", 1, 0, 4, 94),
                ("Halaman Resmi Facebook", "https://facebook.com", "Komunitas dan siaran langsung", "/static/icons/facebook.svg", "Media Sosial", 1, 0, 5, 87),
                ("Konsultasi Langsung via WhatsApp", "https://wa.me/6281234567890", "Layanan respon cepat dan tanya jawab", "/static/icons/whatsapp.svg", "Kontak", 1, 0, 6, 76),
            ]
            for title, url, subtitle, icon, category, is_active, is_highlighted, sort_order, click_count in sample_links:
                conn.execute("""
                    INSERT INTO links (title, url, subtitle, icon, category, is_active, is_highlighted, sort_order, click_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (title, url, subtitle, icon, category, is_active, is_highlighted, sort_order, click_count))

    conn.close()

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        row = conn.execute("SELECT id, username, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def update_user_password(user_id: int, new_password: str) -> bool:
    conn = get_connection()
    try:
        with conn:
            conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(new_password), user_id))
        return True
    except Exception:
        return False
    finally:
        conn.close()

def get_profile() -> Dict[str, Any]:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM profile WHERE id = 1").fetchone()
        if not row:
            init_db()
            row = conn.execute("SELECT * FROM profile WHERE id = 1").fetchone()
        data = dict(row)
        try:
            data["socials_dict"] = json.loads(data.get("socials") or "{}")
        except Exception:
            data["socials_dict"] = {}
        return data
    finally:
        conn.close()

def update_profile(name: str, handle: str, bio: str, avatar_url: str,
                   avatar_size: int, theme: str, socials: dict,
                   footer_text: str, show_share_button: int) -> bool:
    conn = get_connection()
    try:
        socials_json = json.dumps(socials)
        with conn:
            conn.execute("""
                UPDATE profile SET
                    name = ?,
                    handle = ?,
                    bio = ?,
                    avatar_url = ?,
                    avatar_size = ?,
                    theme = ?,
                    socials = ?,
                    footer_text = ?,
                    show_share_button = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
            """, (name, handle, bio, avatar_url, avatar_size, theme, socials_json, footer_text, show_share_button))
        return True
    except Exception:
        return False
    finally:
        conn.close()

def get_links(only_active: bool = False) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        sql = "SELECT * FROM links"
        params = []
        if only_active:
            sql += " WHERE is_active = 1"
        sql += " ORDER BY sort_order ASC, id ASC"
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_link_by_id(link_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM links WHERE id = ?", (link_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def add_link(title: str, url: str, subtitle: str = "", icon: str = "🔗",
             category: str = "", is_active: int = 1, is_highlighted: int = 0) -> int:
    conn = get_connection()
    try:
        with conn:
            # get current highest sort_order
            max_order_row = conn.execute("SELECT COALESCE(MAX(sort_order), -1) AS max_order FROM links").fetchone()
            next_order = max_order_row["max_order"] + 1
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO links (title, url, subtitle, icon, category, is_active, is_highlighted, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, url, subtitle, icon, category, is_active, is_highlighted, next_order))
            return cur.lastrowid
    finally:
        conn.close()

def update_link(link_id: int, title: str, url: str, subtitle: str = "", icon: str = "🔗",
                category: str = "", is_active: int = 1, is_highlighted: int = 0) -> bool:
    conn = get_connection()
    try:
        with conn:
            conn.execute("""
                UPDATE links SET
                    title = ?,
                    url = ?,
                    subtitle = ?,
                    icon = ?,
                    category = ?,
                    is_active = ?,
                    is_highlighted = ?
                WHERE id = 1
            """, (title, url, subtitle, icon, category, is_active, is_highlighted)) if False else None
            conn.execute("""
                UPDATE links SET
                    title = ?,
                    url = ?,
                    subtitle = ?,
                    icon = ?,
                    category = ?,
                    is_active = ?,
                    is_highlighted = ?
                WHERE id = ?
            """, (title, url, subtitle, icon, category, is_active, is_highlighted, link_id))
        return True
    except Exception:
        return False
    finally:
        conn.close()

def toggle_link_status(link_id: int) -> Optional[int]:
    conn = get_connection()
    try:
        with conn:
            row = conn.execute("SELECT is_active FROM links WHERE id = ?", (link_id,)).fetchone()
            if not row:
                return None
            new_status = 0 if row["is_active"] == 1 else 1
            conn.execute("UPDATE links SET is_active = ? WHERE id = ?", (new_status, link_id))
            return new_status
    finally:
        conn.close()

def delete_link(link_id: int) -> bool:
    conn = get_connection()
    try:
        with conn:
            conn.execute("DELETE FROM links WHERE id = ?", (link_id,))
        return True
    except Exception:
        return False
    finally:
        conn.close()

def reorder_links(ordered_ids: List[int]) -> bool:
    conn = get_connection()
    try:
        with conn:
            for index, lid in enumerate(ordered_ids):
                conn.execute("UPDATE links SET sort_order = ? WHERE id = ?", (index, lid))
        return True
    except Exception:
        return False
    finally:
        conn.close()

def record_click(link_id: int, user_agent: str = "", ip_address: str = "") -> Optional[str]:
    conn = get_connection()
    try:
        with conn:
            row = conn.execute("SELECT url FROM links WHERE id = ?", (link_id,)).fetchone()
            if not row:
                return None
            target_url = row["url"]
            conn.execute("UPDATE links SET click_count = click_count + 1 WHERE id = ?", (link_id,))
            conn.execute("""
                INSERT INTO click_logs (link_id, user_agent, ip_address)
                VALUES (?, ?, ?)
            """, (link_id, user_agent[:250], ip_address[:100]))
            return target_url
    finally:
        conn.close()

def get_analytics_summary() -> Dict[str, Any]:
    conn = get_connection()
    try:
        total_links = conn.execute("SELECT COUNT(*) AS cnt FROM links").fetchone()["cnt"]
        active_links = conn.execute("SELECT COUNT(*) AS cnt FROM links WHERE is_active = 1").fetchone()["cnt"]
        total_clicks = conn.execute("SELECT COALESCE(SUM(click_count), 0) AS total FROM links").fetchone()["total"]
        
        top_links_rows = conn.execute("""
            SELECT id, title, url, click_count, icon
            FROM links
            ORDER BY click_count DESC, id ASC
            LIMIT 5
        """).fetchall()
        top_links = [dict(r) for r in top_links_rows]

        recent_clicks_rows = conn.execute("""
            SELECT l.title, c.clicked_at, c.ip_address
            FROM click_logs c
            JOIN links l ON c.link_id = l.id
            ORDER BY c.clicked_at DESC
            LIMIT 10
        """).fetchall()
        recent_clicks = [dict(r) for r in recent_clicks_rows]

        return {
            "total_links": total_links,
            "active_links": active_links,
            "total_clicks": total_clicks,
            "top_links": top_links,
            "recent_clicks": recent_clicks
        }
    finally:
        conn.close()
