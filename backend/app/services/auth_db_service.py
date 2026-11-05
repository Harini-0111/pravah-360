"""
PRAVAH 360 Authentication, Authorization & Session Database Service.
Persistent SQLite store with salted PBKDF2-HMAC-SHA256 password hashing,
HttpOnly session cookies, role-based access control (RBAC),
rate-limited authentication, and audit logging.
"""

import os
import time
import uuid
import hashlib
import secrets
import sqlite3
import html
from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "users.db"))

class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str  # 'citizen', 'mandal_admin', 'district_admin', 'emergency_response'
    district: Optional[str] = "East Godavari"
    mandal: Optional[str] = None
    jurisdiction: Optional[str] = None
    created_at: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    mandal: Optional[str] = "Rajamahendravaram Urban"
    district: Optional[str] = "East Godavari"

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthDBService:
    """Handles SQLite persistence for users, sessions, audit logging, and rate limiting."""

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def init_db(cls):
        """Initializes tables for accounts, sessions, rate-limiting and audit log."""
        conn = cls.get_connection()
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                        password_hash TEXT NOT NULL,
                        role TEXT NOT NULL,
                        full_name TEXT NOT NULL,
                        jurisdiction TEXT,
                        district TEXT DEFAULT 'East Godavari',
                        mandal TEXT,
                        created_at TEXT NOT NULL,
                        is_active INTEGER DEFAULT 1
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        expires_at REAL NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS audit_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        user_id TEXT,
                        action TEXT NOT NULL,
                        ip_address TEXT,
                        details TEXT
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS login_attempts (
                        ip_address TEXT NOT NULL,
                        attempt_time REAL NOT NULL
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_login_attempts ON login_attempts(ip_address, attempt_time)")
        finally:
            conn.close()

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> str:
        """Salted PBKDF2-HMAC-SHA256 with 100,000 iterations using standard library."""
        if not salt:
            salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}${key.hex()}"

    @staticmethod
    def verify_password(plain_password: str, stored_hash: str) -> bool:
        try:
            salt, hash_val = stored_hash.split('$', 1)
            candidate = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
            return secrets.compare_digest(candidate, hash_val)
        except Exception:
            return False

    @classmethod
    def sanitize(cls, text: Optional[str]) -> Optional[str]:
        if text is None:
            return None
        return html.escape(text.strip())

    @classmethod
    def log_audit(cls, action: str, user_id: Optional[str] = None, ip: Optional[str] = None, details: Optional[str] = None):
        conn = cls.get_connection()
        try:
            with conn:
                conn.execute(
                    "INSERT INTO audit_log (timestamp, user_id, action, ip_address, details) VALUES (?, ?, ?, ?, ?)",
                    (time.time(), user_id, action, ip or "127.0.0.1", details or "")
                )
        except Exception as e:
            print(f"Audit log notice: {e}")
        finally:
            conn.close()

    @classmethod
    def check_rate_limit(cls, ip: str, max_attempts: int = 5, window_seconds: int = 300) -> bool:
        """Returns True if request is allowed, False if rate limited."""
        now = time.time()
        cutoff = now - window_seconds
        conn = cls.get_connection()
        try:
            with conn:
                # Purge old attempts
                conn.execute("DELETE FROM login_attempts WHERE attempt_time < ?", (cutoff,))
                cursor = conn.execute("SELECT COUNT(*) FROM login_attempts WHERE ip_address = ?", (ip,))
                count = cursor.fetchone()[0]
                return count < max_attempts
        finally:
            conn.close()

    @classmethod
    def record_failed_attempt(cls, ip: str):
        conn = cls.get_connection()
        try:
            with conn:
                conn.execute("INSERT INTO login_attempts (ip_address, attempt_time) VALUES (?, ?)", (ip, time.time()))
        finally:
            conn.close()

    @classmethod
    def create_user(
        cls,
        email: str,
        password: str,
        full_name: str,
        role: str,
        district: Optional[str] = "East Godavari",
        mandal: Optional[str] = None,
        jurisdiction: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Creates an account with role validation. Citizen accounts can self-register; privileged accounts via script."""
        valid_roles = ["citizen", "mandal_admin", "district_admin", "emergency_response"]
        clean_role = role.strip().lower()
        if clean_role not in valid_roles:
            return False, f"Invalid role: '{clean_role}'. Must be one of {valid_roles}.", None

        clean_email = email.strip().lower()
        if not clean_email or "@" not in clean_email:
            return False, "A valid email address is required.", None

        if len(password) < 8:
            return False, "Password must be at least 8 characters long.", None

        conn = cls.get_connection()
        try:
            cursor = conn.execute("SELECT user_id FROM users WHERE email = ?", (clean_email,))
            if cursor.fetchone():
                return False, f"An account with email '{clean_email}' already exists.", None

            user_id = f"usr-{clean_role[:3]}-{secrets.token_hex(4)}"
            pwd_hash = cls.hash_password(password)
            now_iso = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

            with conn:
                conn.execute("""
                    INSERT INTO users (user_id, email, password_hash, role, full_name, jurisdiction, district, mandal, created_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (
                    user_id,
                    clean_email,
                    pwd_hash,
                    clean_role,
                    cls.sanitize(full_name),
                    cls.sanitize(jurisdiction),
                    cls.sanitize(district),
                    cls.sanitize(mandal),
                    now_iso
                ))

            cls.log_audit("USER_CREATED", user_id=user_id, details=f"Created user {clean_email} with role {clean_role}")
            user_data = {
                "user_id": user_id,
                "email": clean_email,
                "full_name": full_name,
                "role": clean_role,
                "district": district,
                "mandal": mandal,
                "jurisdiction": jurisdiction,
                "created_at": now_iso
            }
            return True, "User successfully created.", user_data
        finally:
            conn.close()

    @classmethod
    def authenticate(cls, email: str, password: str, ip: str = "127.0.0.1") -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        if not cls.check_rate_limit(ip):
            cls.log_audit("LOGIN_RATE_LIMITED", ip=ip, details=f"Exceeded attempt threshold for {email}")
            return False, "Too many failed login attempts. Please wait 5 minutes before retrying.", None

        clean_email = email.strip().lower()
        conn = cls.get_connection()
        try:
            cursor = conn.execute("SELECT * FROM users WHERE email = ? AND is_active = 1", (clean_email,))
            row = cursor.fetchone()
            if not row:
                cls.record_failed_attempt(ip)
                cls.log_audit("LOGIN_FAILED", ip=ip, details=f"User not found: {clean_email}")
                return False, "Invalid email address or password.", None

            if not cls.verify_password(password, row["password_hash"]):
                cls.record_failed_attempt(ip)
                cls.log_audit("LOGIN_FAILED", user_id=row["user_id"], ip=ip, details="Incorrect password")
                return False, "Invalid email address or password.", None

            # Create session
            session_id = "prv_" + secrets.token_urlsafe(32)
            now = time.time()
            expires_at = now + 86400  # 24 hour TTL

            with conn:
                conn.execute(
                    "INSERT INTO sessions (session_id, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
                    (session_id, row["user_id"], now, expires_at)
                )

            cls.log_audit("LOGIN_SUCCESS", user_id=row["user_id"], ip=ip, details=f"Session established ({row['role']})")
            user_data = {
                "session_id": session_id,
                "expires_at": expires_at,
                "user": {
                    "user_id": row["user_id"],
                    "email": row["email"],
                    "full_name": row["full_name"],
                    "role": row["role"],
                    "district": row["district"],
                    "mandal": row["mandal"],
                    "jurisdiction": row["jurisdiction"],
                    "created_at": row["created_at"]
                }
            }
            return True, "Login successful.", user_data
        finally:
            conn.close()

    @classmethod
    def get_user_from_session(cls, session_id: str) -> Optional[Dict[str, Any]]:
        if not session_id:
            return None
        conn = cls.get_connection()
        try:
            now = time.time()
            cursor = conn.execute("""
                SELECT u.* FROM sessions s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.session_id = ? AND s.expires_at > ? AND u.is_active = 1
            """, (session_id, now))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "user_id": row["user_id"],
                "email": row["email"],
                "full_name": row["full_name"],
                "role": row["role"],
                "district": row["district"],
                "mandal": row["mandal"],
                "jurisdiction": row["jurisdiction"],
                "created_at": row["created_at"]
            }
        finally:
            conn.close()

    @classmethod
    def invalidate_session(cls, session_id: str, ip: str = "127.0.0.1") -> bool:
        if not session_id:
            return False
        conn = cls.get_connection()
        try:
            with conn:
                cursor = conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                deleted = cursor.rowcount > 0
                if deleted:
                    cls.log_audit("LOGOUT", ip=ip, details=f"Terminated session {session_id[:12]}...")
                return deleted
        finally:
            conn.close()

# Auto-initialize database tables on module import
AuthDBService.init_db()
