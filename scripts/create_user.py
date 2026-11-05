#!/usr/bin/env python3
"""
PRAVAH 360 Privileged Account Provisioning CLI.
Creates administrative and emergency response accounts server-side.
Does not ship or hardcode default passwords; prompts securely via getpass.
"""

import sys
import os
import argparse
import getpass

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.services.auth_db_service import AuthDBService

def main():
    parser = argparse.ArgumentParser(description="Create a PRAVAH 360 user account (privileged or citizen).")
    parser.add_argument("--email", required=True, help="User's official email address")
    parser.add_argument("--role", required=True, choices=["citizen", "mandal_admin", "district_admin", "emergency_response"], help="System authorization role")
    parser.add_argument("--name", required=True, help="Full name of official or citizen")
    parser.add_argument("--district", default="East Godavari", help="Assigned administrative district")
    parser.add_argument("--mandal", default=None, help="Assigned administrative mandal")
    parser.add_argument("--jurisdiction", default=None, help="Assigned office or jurisdiction description")
    parser.add_argument("--password", default=None, help="Password (optional flag; if omitted, securely prompted)")

    args = parser.parse_args()

    pwd = args.password
    if not pwd:
        pwd = getpass.getpass(f"Enter password for {args.email} (min 8 chars): ")
        pwd_confirm = getpass.getpass("Confirm password: ")
        if pwd != pwd_confirm:
            print("Error: Passwords do not match.", file=sys.stderr)
            sys.exit(1)

    success, msg, user_data = AuthDBService.create_user(
        email=args.email,
        password=pwd,
        full_name=args.name,
        role=args.role,
        district=args.district,
        mandal=args.mandal,
        jurisdiction=args.jurisdiction
    )

    if success:
        print(f"SUCCESS: Account created for {user_data['full_name']} ({user_data['email']}) with role '{user_data['role']}'.")
        print(f"User ID: {user_data['user_id']}")
        sys.exit(0)
    else:
        print(f"ERROR: {msg}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
