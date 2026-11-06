#!/usr/bin/env python3
"""
Seed Initial Demo Users and Organization into TenderForge Database.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.infrastructure.database.session import SessionLocal
from backend.app.api.schemas.auth import UserRegisterRequest
from backend.app.services.auth_service import AuthService
from backend.app.infrastructure.database.models import User


def seed_demo_users():
    db = SessionLocal()
    try:
        users_data = [
            {
                "email": "admin@tenderforge.com",
                "password": "TenderForgeAdmin2026!",
                "full_name": "TenderForge Administrator",
                "role": "Admin",
                "organization_name": "Apex Global Defense",
            },
            {
                "email": "author@tenderforge.com",
                "password": "TenderForgeAuthor2026!",
                "full_name": "Sarah Jenkins (Lead Architect)",
                "role": "Author",
                "organization_name": "Apex Global Defense",
            },
            {
                "email": "reviewer@tenderforge.com",
                "password": "TenderForgeReviewer2026!",
                "full_name": "David Vance (Compliance Auditor)",
                "role": "Reviewer",
                "organization_name": "Apex Global Defense",
            },
        ]

        print("Seeding demo accounts into database...")
        for u in users_data:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                req = UserRegisterRequest(**u)
                user, token = AuthService.register_user(db, req)
                print(f"  + Created: {user.email} (Role: {user.role}, ID: {user.id})")
            else:
                print(f"  * Already exists: {existing.email} (Role: {existing.role})")

        print("Demo seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_users()
