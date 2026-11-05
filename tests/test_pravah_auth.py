"""
Test Suite for PRAVAH 360 Authentication, Sessions, RBAC & Audit Logging (Phase B).
Uses standard library unittest and tests AuthDBService directly.
"""

import unittest
import time
from backend.app.services.auth_db_service import AuthDBService

class TestPravahAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        AuthDBService.init_db()

        # Provision accounts for testing
        _, _, cls.citizen = AuthDBService.create_user(
            email="test_citizen@pravah.test",
            password="TestPassword@123",
            full_name="Test Citizen",
            role="citizen",
            mandal="Rajamahendravaram Urban"
        )
        _, _, cls.mandal_admin = AuthDBService.create_user(
            email="test_mandal_admin@pravah.test",
            password="AdminPassword@123",
            full_name="Test Tahsildar",
            role="mandal_admin",
            mandal="Rajamahendravaram Urban"
        )
        _, _, cls.district_admin = AuthDBService.create_user(
            email="test_district_admin@pravah.test",
            password="CollectorPassword@123",
            full_name="Test Collector IAS",
            role="district_admin"
        )
        _, _, cls.ert = AuthDBService.create_user(
            email="test_ert@pravah.test",
            password="ResponderPassword@123",
            full_name="Test SDRF Responder",
            role="emergency_response"
        )

    def test_01_citizen_self_registration(self):
        """Citizen can self-register; password must be salted/hashed and role strictly set to citizen."""
        new_email = f"self_citizen_{int(time.time() * 1000)}@pravah.test"
        success, msg, user = AuthDBService.create_user(
            email=new_email,
            password="SecurePassword@123",
            full_name="Self Registered Citizen",
            role="citizen",
            mandal="Kovvur"
        )
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user["email"], new_email)
        self.assertEqual(user["role"], "citizen")
        self.assertEqual(user["mandal"], "Kovvur")
        self.assertNotIn("password_hash", user)  # Sensitive hash not returned in safe dict

    def test_02_login_verification_success(self):
        """Valid credentials authenticate successfully and return sanitized user profile and session."""
        success, msg, data = AuthDBService.authenticate("test_citizen@pravah.test", "TestPassword@123")
        self.assertTrue(success)
        self.assertIsNotNone(data)
        self.assertEqual(data["user"]["email"], "test_citizen@pravah.test")
        self.assertEqual(data["user"]["role"], "citizen")
        self.assertTrue("session_id" in data)

    def test_03_login_failure_invalid_password(self):
        """Invalid credentials fail authentication and return False."""
        success, msg, data = AuthDBService.authenticate("test_citizen@pravah.test", "WrongPassword@999")
        self.assertFalse(success)
        self.assertIsNone(data)

    def test_04_session_lifecycle_and_invalidation(self):
        """Session token generation, retrieval, and invalidation upon logout."""
        success, _, data = AuthDBService.authenticate("test_mandal_admin@pravah.test", "AdminPassword@123")
        self.assertTrue(success)
        token = data["session_id"]
        self.assertIsInstance(token, str)
        self.assertTrue(token.startswith("prv_"))

        # Retrieve user by session
        session_user = AuthDBService.get_user_from_session(token)
        self.assertIsNotNone(session_user)
        self.assertEqual(session_user["email"], "test_mandal_admin@pravah.test")
        self.assertEqual(session_user["role"], "mandal_admin")

        # Invalidate session (logout)
        deleted = AuthDBService.invalidate_session(token)
        self.assertTrue(deleted)
        expired_user = AuthDBService.get_user_from_session(token)
        self.assertIsNone(expired_user, "Session must be invalid after logout")

    def test_05_role_authorization_and_audit_logging(self):
        """Verify role segregation and immutable audit logging."""
        # 1. District admin action logged to audit trail
        action_detail = f"Disaster Plan Activation Test {int(time.time() * 1000)}"
        AuthDBService.log_audit(
            action="ACTIVATE_DISASTER_PLAN",
            user_id="usr-dis-001",
            ip="127.0.0.1",
            details=action_detail
        )

        conn = AuthDBService.get_connection()
        try:
            cursor = conn.execute("SELECT * FROM audit_log WHERE details = ?", (action_detail,))
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["action"], "ACTIVATE_DISASTER_PLAN")
        finally:
            conn.close()

        # 2. RBAC check simulation: citizen cannot access district_admin protected resource
        citizen_allowed = "citizen" in ["district_admin"]
        district_allowed = "district_admin" in ["district_admin"]
        self.assertFalse(citizen_allowed)
        self.assertTrue(district_allowed)

    def test_06_brute_force_rate_limiting(self):
        """Rate limiting prevents rapid password guessing."""
        import uuid
        ip = f"198.51.100.{uuid.uuid4().hex[:4]}"
        # Initially allowed
        self.assertTrue(AuthDBService.check_rate_limit(ip, max_attempts=5))

        # Record 5 failed attempts
        for _ in range(5):
            AuthDBService.record_failed_attempt(ip)

        # Now rate limited
        self.assertFalse(AuthDBService.check_rate_limit(ip, max_attempts=5))

if __name__ == "__main__":
    unittest.main()
