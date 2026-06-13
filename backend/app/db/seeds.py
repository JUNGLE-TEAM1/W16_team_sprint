from sqlalchemy.orm import Session

from backend.app.core.security import hash_password
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository


def seed_demo_users(database_engine) -> None:
    with Session(database_engine) as db:
        users = UserRepository(db)
        demo_users = [
            {
                "email": "member@sprint.local",
                "password": "password123",
                "role": "member",
            },
            {
                "email": "admin@sprint.local",
                "password": "admin123",
                "role": "admin",
            },
        ]

        for demo_user in demo_users:
            if users.get_by_email(demo_user["email"]) is None:
                users.create(
                    User(
                        email=demo_user["email"],
                        password_hash=hash_password(demo_user["password"]),
                        role=demo_user["role"],
                    )
                )

        db.commit()
