import sys
import os
sys.path.insert(0, os.path.abspath(r"C:\major project"))

from backend.app.services.auth_db_service import AuthDBService

demo_users = [
    {
        "email": "citizen@pravah360.in",
        "password": "Citizen@123",
        "full_name": "Ramesh Varma",
        "role": "citizen",
        "district": "East Godavari",
        "mandal": "Rajamahendravaram Urban"
    },
    {
        "email": "mandal.admin@pravah360.in",
        "password": "Mandal@123",
        "full_name": "Tahsildar Satyanarayana",
        "role": "mandal_admin",
        "district": "East Godavari",
        "mandal": "Rajamahendravaram Urban"
    },
    {
        "email": "district.collector@pravah360.in",
        "password": "District@123",
        "full_name": "Collector Madhavilatha, IAS",
        "role": "district_admin",
        "district": "East Godavari",
        "jurisdiction": "East Godavari Collectorate"
    },
    {
        "email": "ert.commander@pravah360.in",
        "password": "Responder@123",
        "full_name": "Inspector Prasad",
        "role": "emergency_response",
        "district": "East Godavari",
        "jurisdiction": "3rd Battalion SDRF Delta Quick Response"
    }
]

AuthDBService.init_db()
for u in demo_users:
    success, msg, data = AuthDBService.create_user(
        email=u["email"],
        password=u["password"],
        full_name=u["full_name"],
        role=u["role"],
        district=u.get("district"),
        mandal=u.get("mandal"),
        jurisdiction=u.get("jurisdiction")
    )
    print(f"Seed {u['email']}: success={success}, msg={msg}")
