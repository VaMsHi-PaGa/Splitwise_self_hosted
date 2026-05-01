"""
Create a user from the command line.

Usage:
  docker compose exec backend python create_user.py <email> <password> [name]

Example:
  docker compose exec backend python create_user.py test@test.com test123 "Test User"
"""
import sys

from app.database import SessionLocal
from app.models.user import User
from app.security import hash_password


def main():
    if len(sys.argv) < 3:
        print("Usage: python create_user.py <email> <password> [name]")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else email.split("@")[0]

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User {email} already exists")
            sys.exit(1)

        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
        )
        db.add(user)
        db.commit()
        print(f"Created user: {email} (id: {user.id})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
