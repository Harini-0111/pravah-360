"""
PRAVAH 360 Authentication & Session Management Service.
Provides cryptographic password hashing, role-based authorization,
session lifecycle tracking, and demo authentication environment.
"""

import os
import time
import uuid
import hashlib
import secrets
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str  # 'citizen', 'mandal_admin', 'district_admin', 'ert'
    jurisdiction: Optional[str] = None
    district: Optional[str] = "East Godavari"
    mandal: Optional[str] = None
    badge_number: Optional[str] = None
    created_at: float = Field(default_factory=time.time)

class AuthSession(BaseModel):
    token: str
    user: UserProfile
    created_at: float
    expires_at: float
    environment: str = "PRAVAH 360 Demonstration & Evaluation Environment"

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthService:
    """Manages secure password hashing and role-based session tokens."""
    
    # In-memory session store (can persist to disk if needed)
    _sessions: Dict[str, AuthSession] = {}
    SESSION_TTL_SECONDS = 86400  # 24 hours

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> str:
        """PBKDF2-HMAC-SHA256 hash using 100,000 iterations."""
        if not salt:
            salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}${key.hex()}"

    @staticmethod
    def verify_password(plain_password: str, stored_hash: str) -> bool:
        try:
            salt, hash_val = stored_hash.split('$', 1)
            candidate_key = hashlib.pbkdf2_hmac(
                'sha256',
                plain_password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            ).hex()
            return secrets.compare_digest(candidate_key, hash_val)
        except Exception:
            return False

    # Seed demonstration user registry with pre-hashed credentials
    DEMO_USERS: Dict[str, Dict[str, Any]] = {
        "citizen@pravah360.in": {
            "user_id": "usr-cit-001",
            "email": "citizen@pravah360.in",
            "password_hash": hash_password("Citizen@123", "pravah_cit_salt"),
            "full_name": "Ramesh Varma",
            "role": "citizen",
            "district": "East Godavari",
            "mandal": "Rajamahendravaram Urban",
            "jurisdiction": "Ward 14, Rajamahendravaram Urban"
        },
        "mandal.admin@pravah360.in": {
            "user_id": "usr-mnd-002",
            "email": "mandal.admin@pravah360.in",
            "password_hash": hash_password("Mandal@123", "pravah_mnd_salt"),
            "full_name": "K. Satyanarayana (Tahsildar)",
            "role": "mandal_admin",
            "district": "East Godavari",
            "mandal": "Rajamahendravaram Urban",
            "jurisdiction": "Rajamahendravaram Urban Mandal Revenue Office"
        },
        "district.collector@pravah360.in": {
            "user_id": "usr-dst-003",
            "email": "district.collector@pravah360.in",
            "password_hash": hash_password("District@123", "pravah_dst_salt"),
            "full_name": "Dr. K. Madhavilatha, IAS",
            "role": "district_admin",
            "district": "East Godavari",
            "mandal": None,
            "jurisdiction": "East Godavari District Disaster Management Authority (DDMA)"
        },
        "ert.commander@pravah360.in": {
            "user_id": "usr-ert-004",
            "email": "ert.commander@pravah360.in",
            "password_hash": hash_password("Responder@123", "pravah_ert_salt"),
            "full_name": "Inspector D. Prasad",
            "role": "ert",
            "district": "East Godavari",
            "mandal": "Rajamahendravaram",
            "badge_number": "SDRF-AP-BN3-042",
            "jurisdiction": "State Disaster Response Force • Battalion 3 Quick Response Post"
        }
    }

    @classmethod
    def authenticate_user(cls, email: str, password: str) -> Optional[UserProfile]:
        user_record = cls.DEMO_USERS.get(email.strip().lower())
        if not user_record:
            return None
        if not cls.verify_password(password, user_record["password_hash"]):
            return None
        
        return UserProfile(
            user_id=user_record["user_id"],
            email=user_record["email"],
            full_name=user_record["full_name"],
            role=user_record["role"],
            district=user_record.get("district"),
            mandal=user_record.get("mandal"),
            jurisdiction=user_record.get("jurisdiction"),
            badge_number=user_record.get("badge_number")
        )

    @classmethod
    def create_session(cls, user: UserProfile) -> AuthSession:
        token = "prv_" + secrets.token_urlsafe(32)
        now = time.time()
        session = AuthSession(
            token=token,
            user=user,
            created_at=now,
            expires_at=now + cls.SESSION_TTL_SECONDS
        )
        cls._sessions[token] = session
        return session

    @classmethod
    def get_session(cls, token: str) -> Optional[AuthSession]:
        session = cls._sessions.get(token)
        if not session:
            return None
        if time.time() > session.expires_at:
            del cls._sessions[token]
            return None
        return session

    @classmethod
    def invalidate_session(cls, token: str) -> bool:
        if token in cls._sessions:
            del cls._sessions[token]
            return True
        return False

    @classmethod
    def list_demo_accounts(cls) -> List[Dict[str, str]]:
        return [
            {
                "role": "citizen",
                "label": "Citizen",
                "email": "citizen@pravah360.in",
                "password": "Citizen@123",
                "name": "Ramesh Varma",
                "scope": "Rajamahendravaram Urban Mandal"
            },
            {
                "role": "mandal_admin",
                "label": "Mandal Administrator",
                "email": "mandal.admin@pravah360.in",
                "password": "Mandal@123",
                "name": "K. Satyanarayana (Tahsildar)",
                "scope": "Rajamahendravaram Urban Mandal"
            },
            {
                "role": "district_admin",
                "label": "District Administrator",
                "email": "district.collector@pravah360.in",
                "password": "District@123",
                "name": "Dr. K. Madhavilatha, IAS",
                "scope": "East Godavari District DDMA"
            },
            {
                "role": "ert",
                "label": "Emergency Response Team",
                "email": "ert.commander@pravah360.in",
                "password": "Responder@123",
                "name": "Inspector D. Prasad (SDRF)",
                "scope": "State Disaster Response Force AP"
            }
        ]
